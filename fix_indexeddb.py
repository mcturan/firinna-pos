import re

with open("/opt/firinna-pos/templates/tv_player.html", "r") as f:
    content = f.read()

old_func = """        async function checkAndLoadPersistentVideo(videoUrl) {
            return new Promise((resolve) => {
                if (!db) { resolve(null); return; }
                const tx = db.transaction(STORE_NAME, 'readonly');
                const store = tx.objectStore(STORE_NAME);
                const req = store.get(videoUrl);
                req.onsuccess = () => {
                    if (req.result && req.result.blob) {
                        const blob = req.result.blob;
                        const sizeMB = (blob.size / (1024*1024)).toFixed(1);
                        tvLog(`[CACHE STORAGE HIT] ${videoUrl.split('/').pop()} (${sizeMB} MB) loaded from persistent disk cache!`);
                        const objUrl = URL.createObjectURL(blob);
                        bufferedVideoBlobs[videoUrl] = objUrl;
                        resolve(objUrl);
                    } else {
                        resolve(null);
                    }
                };
                req.onerror = () => resolve(null);
            });
        }"""

new_func = """        async function checkAndLoadPersistentVideo(videoUrl) {
            return new Promise((resolve) => {
                if (!db) { resolve(null); return; }
                const tx = db.transaction(STORE_NAME, 'readwrite');
                const store = tx.objectStore(STORE_NAME);
                const req = store.get(videoUrl);
                req.onsuccess = () => {
                    if (req.result && req.result.blob) {
                        const blob = req.result.blob;
                        const sizeMB = (blob.size / (1024*1024)).toFixed(1);
                        
                        // SAFETY: If the cached file is larger than 250MB, it will crash the TV RAM on load.
                        if (blob.size > 250 * 1024 * 1024) {
                            tvLog(`[CACHE PURGE] ${videoUrl.split('/').pop()} (${sizeMB} MB) is too large for TV RAM. Deleting from IndexedDB to prevent crash.`);
                            store.delete(videoUrl);
                            resolve(null);
                            return;
                        }
                        
                        tvLog(`[CACHE STORAGE HIT] ${videoUrl.split('/').pop()} (${sizeMB} MB) loaded from persistent disk cache!`);
                        const objUrl = URL.createObjectURL(blob);
                        bufferedVideoBlobs[videoUrl] = objUrl;
                        resolve(objUrl);
                    } else {
                        resolve(null);
                    }
                };
                req.onerror = () => resolve(null);
            });
        }"""

content = content.replace(old_func, new_func)

with open("/opt/firinna-pos/templates/tv_player.html", "w") as f:
    f.write(content)
