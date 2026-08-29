import re

with open("/opt/firinna-pos/templates/tv_player.html", "r") as f:
    content = f.read()

# 1. Remove streamOnlyVideos logic from playLocalVideo
old_play = """            // 1. Safety Check: If marked as stream-only (due to large size), stream directly
            if (window.streamOnlyVideos && window.streamOnlyVideos[srcUrl]) {
                isPlayingFallback = false;
                tvLog(`[PLAYBACK STREAM] File too large for RAM cache. Streaming directly: ${filename}`);
                playBlobDirectly(srcUrl, srcUrl);
                return;
            }"""
content = content.replace(old_play, "")

# 2. Revert processBackgroundDownloadQueue completely
old_process = """        window.streamOnlyVideos = {};

        async function processBackgroundDownloadQueue() {
            if (isDownloadingVideo || videoDownloadQueue.length === 0) return;
            const targetUrl = videoDownloadQueue.shift();
            const filename = targetUrl.split('/').pop();
            
            // Re-verify if already cached
            const cachedBlobUrl = await checkAndLoadPersistentVideo(targetUrl);
            if (cachedBlobUrl) {
                processBackgroundDownloadQueue();
                return;
            }
            
            // SAFETY MECHANISM: Check file size before downloading to prevent RAM OOM Crash
            try {
                const headRes = await fetch(targetUrl, { method: 'HEAD' });
                const size = headRes.headers.get('content-length');
                if (size) {
                    const sizeMB = (parseInt(size) / (1024 * 1024)).toFixed(1);
                    if (parseInt(size) > 150 * 1024 * 1024) { // 150 MB LIMIT
                        tvLog(`[SAFETY GUARD] ${filename} is ${sizeMB}MB (>150MB). Skipping cache to prevent RAM crash. Marked for direct streaming.`);
                        window.streamOnlyVideos[targetUrl] = true;
                        processBackgroundDownloadQueue();
                        return;
                    }
                }
            } catch(e) {
                tvLog(`[SAFETY GUARD] Could not verify size for ${filename}, proceeding with caution.`);
            }

            const filename = targetUrl.split('/').pop();"""

new_process = """        async function processBackgroundDownloadQueue() {
            if (isDownloadingVideo || videoDownloadQueue.length === 0) return;
            const targetUrl = videoDownloadQueue.shift();
            
            // Re-verify if already cached
            const cachedBlobUrl = await checkAndLoadPersistentVideo(targetUrl);
            if (cachedBlobUrl) {
                processBackgroundDownloadQueue();
                return;
            }

            const filename = targetUrl.split('/').pop();"""

content = content.replace(old_process, new_process)

with open("/opt/firinna-pos/templates/tv_player.html", "w") as f:
    f.write(content)
