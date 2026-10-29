"""Instagram API (Instagram Login) ile paylaşım."""
import os
import time
import requests

def _graph(token):
    """IGAA... ile başlayan token'lar Instagram girişiyle, EAA... ile başlayanlar Facebook girişiyle alınmıştır."""
    if token.startswith("EAA"):
        return "https://graph.facebook.com/v23.0"
    return "https://graph.instagram.com/v23.0"


class Instagram:
    def __init__(self, token=None, user_id=None):
        self.token = (token or os.environ["IG_TOKEN"]).strip().strip('"').strip("'")
        self.user_id = (user_id or os.environ["IG_USER_ID"]).strip()
        self.graph = _graph(self.token)
        # Instagram girişli token'larda hesap "me" ile adreslenir (ID karışıklığını önler)
        self.hedef = "me" if "graph.instagram.com" in self.graph else self.user_id

    def tani(self):
        """Token'ın hangi hesaba ait olduğunu döner (token'ı göstermez)."""
        fields = "user_id,username,account_type" if self.hedef == "me" else "username"
        r = requests.get(f"{self.graph}/{self.hedef}", params={"fields": fields, "access_token": self.token}, timeout=30)
        return {"tur": "Instagram girişi" if self.hedef == "me" else "Facebook girişi",
                "durum": r.status_code, "yanit": r.json()}

    def _post(self, path, **data):
        data["access_token"] = self.token
        r = requests.post(f"{self.graph}/{path}", data=data, timeout=60)
        if not r.ok:
            raise RuntimeError(f"Instagram hata {r.status_code}: {r.text[:500]}")
        return r.json()

    def _wait(self, container_id, timeout=180):
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = requests.get(f"{self.graph}/{container_id}",
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
            c = self._post(f"{self.hedef}/media", image_url=image_urls[0], caption=caption)["id"]
        else:
            children = []
            for url in image_urls[:10]:
                cid = self._post(f"{self.hedef}/media", image_url=url, is_carousel_item="true")["id"]
                self._wait(cid)
                children.append(cid)
            c = self._post(f"{self.hedef}/media", media_type="CAROUSEL",
                           children=",".join(children), caption=caption)["id"]
        self._wait(c)
        return self._post(f"{self.hedef}/media_publish", creation_id=c)["id"]


def refresh_token(token):
    """60 günlük token'ı yeniler (token en az 24 saatlik olmalı)."""
    r = requests.get("https://graph.instagram.com/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token.strip()}, timeout=30)
    r.raise_for_status()
    return r.json()
