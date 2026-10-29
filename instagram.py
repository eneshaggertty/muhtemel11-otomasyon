"""Instagram API (Instagram Login) ile paylaşım."""
import os
import time
import requests

GRAPH = "https://graph.instagram.com/v23.0"


class Instagram:
    def __init__(self, token=None, user_id=None):
        self.token = (token or os.environ["IG_TOKEN"]).strip()
        self.user_id = (user_id or os.environ["IG_USER_ID"]).strip()

    def _post(self, path, **data):
        data["access_token"] = self.token
        r = requests.post(f"{GRAPH}/{path}", data=data, timeout=60)
        if not r.ok:
            raise RuntimeError(f"Instagram hata {r.status_code}: {r.text[:500]}")
        return r.json()

    def _wait(self, container_id, timeout=180):
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = requests.get(f"{GRAPH}/{container_id}",
                             params={"fields": "status_code", "access_token": self.token}, timeout=30)
            status = r.json().get("status_code")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise RuntimeError(f"Instagram medya işlenemedi: {r.text[:300]}")
            time.sleep(5)
        raise TimeoutError("Instagram medya işleme zaman aşımı")

    def publish(self, image_urls, caption):
        """Tek görsel ya da carousel paylaşır. Paylaşılan medya ID'sini döner."""
        if len(image_urls) == 1:
            c = self._post(f"{self.user_id}/media", image_url=image_urls[0], caption=caption)["id"]
        else:
            children = []
            for url in image_urls[:10]:
                cid = self._post(f"{self.user_id}/media", image_url=url, is_carousel_item="true")["id"]
                self._wait(cid)
                children.append(cid)
            c = self._post(f"{self.user_id}/media", media_type="CAROUSEL",
                           children=",".join(children), caption=caption)["id"]
        self._wait(c)
        return self._post(f"{self.user_id}/media_publish", creation_id=c)["id"]


def refresh_token(token):
    """60 günlük token'ı yeniler (token en az 24 saatlik olmalı)."""
    r = requests.get("https://graph.instagram.com/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token.strip()}, timeout=30)
    r.raise_for_status()
    return r.json()
