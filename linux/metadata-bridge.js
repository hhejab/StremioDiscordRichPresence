// Read Stremio's already-loaded player model. This bridge performs no network requests.
const enrichDiscordMetadata = (() => {
    let revision = 0;
    return (message, post) => {
        let event;
        try { event = JSON.parse(message); } catch (_) { return; }
        if (event.type !== 6 || event.args?.[0] !== 'media.metadata') return;
        const media = event.args[1];
        if (!media || typeof media.title !== 'string') return;
        const currentRevision = ++revision;
        const hash = location.hash;
        const emit = value => {
            if (revision === currentRevision && location.hash === hash) {
                post(JSON.stringify({type:6,args:['discord-media-context',value]}));
            }
        };
        // Some custom/test frontends only supply the standard media metadata.
        if (typeof window.core?.getState !== 'function') return;
        Promise.resolve().then(() => window.core.getState('player')).then(player => {
            if (player?.metaItem?.type !== 'Ready') return;
            const meta = player.metaItem.content;
            const selected = player.selected;
            const id = selected?.metaRequest?.path?.id || meta?.id;
            const videoId = selected?.streamRequest?.path?.id || id;
            const mediaType = selected?.metaRequest?.path?.type || meta?.type;
            if (!meta || typeof id !== 'string' || typeof videoId !== 'string') return;
            // A delayed snapshot must not enrich metadata for a different episode.
            let route;
            try { route = hash.split('?')[0].replace(/^#\/?/, '').split('/').map(decodeURIComponent); }
            catch (_) { return; }
            if (route[0] === 'player' && route.length === 7 && (route[5] !== id || route[6] !== videoId)) return;
            const video = Array.isArray(meta.videos) ? meta.videos.find(video => video.id === videoId) : null;
            const numbers = videoId.split(':');
            const season = video?.season ?? numbers[1];
            const episode = video?.episode ?? numbers[2];
            const suffix = mediaType === 'series' && /^\d+$/.test(String(season)) && /^\d+$/.test(String(episode)) ? `S${season} · E${episode}` : null;
            const title = video?.title || video?.name || (media.artist ? media.title.replace(/\s*\(\d+x\d+\)$/, '') : null);
            emit({
                id, videoId, mediaType,
                name: typeof meta.name === 'string' ? meta.name : media.artist || media.title,
                episode: title ? `${title}${suffix ? ` (${suffix})` : ''}` : suffix,
                year: String(meta.releaseInfo || meta.year || ''),
                poster: typeof meta.poster === 'string' ? meta.poster : null,
                thumbnail: typeof video?.thumbnail === 'string' ? video.thumbnail : null,
            });
        }).catch(() => {}); // Core reloads must not interrupt playback or basic presence.
    };
})();
