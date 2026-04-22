window.loadList = function() {
    var c = document.getElementById('list-container');
    if (!c) return;
    
    c.innerHTML = '<div class="empty-state"><div class="spinner" style="margin:0 auto"></div><p>Betöltés...</p></div>';
    
    getDocs(collection(db,"szivarozok")).then(function(snap) {
        try {
            allShops = [];
            var latestDate = null;
            
            snap.forEach(function(doc){
                try {
                    var s = doc.data();
                    if (s.source === 'user_submit' && !s.megerositve) return;
                    allShops.push(s);
                    if (s.datum) {
                        var d = new Date(s.datum);
                        if (!latestDate || d > latestDate) latestDate = d;
                    }
                } catch (e) {
                    console.warn('Hibás adat:', e);
                }
            });

            var updBar = document.getElementById('last-updated-bar');
            if (updBar) {
                if (latestDate) {
                    updBar.textContent = '🕐 Utolsó bolt beküldve: ' + latestDate.toLocaleDateString('hu-HU');
                } else {
                    updBar.textContent = '';
                }
            }

            // Biztonságos renderelés kis késleltetéssel
            setTimeout(() => {
                try {
                    renderList(allShops);
                } catch (e) {
                    console.error('Render error:', e);
                    c.innerHTML = '<div class="empty-state">❌ Hiba a megjelenítésben</div>';
                }
            }, 50);
            
        } catch (e) {
            c.innerHTML = '<p style="text-align:center;color:#e55;padding:20px">❌ ' + e.message + '</p>';
        }
    }).catch(function(e){ 
        c.innerHTML = '<p style="text-align:center;color:#e55;padding:20px">❌ ' + e.message + '</p>';
    });
};