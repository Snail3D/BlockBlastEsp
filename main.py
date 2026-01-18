# Block Blast ESP32 - Main Server
# Creates AP and serves the game (memory optimized)

try:
    import usocket as socket
except:
    import socket

import network
import gc

# Access Point Configuration
AP_SSID = "BlockBlast"
AP_PASSWORD = "playblockblast"
AP_IP = "192.168.4.1"

# Optimized HTML with line clearing, unique colors, no 1x1 pieces, better aesthetics
HTML = """<!DOCTYPE html><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Blast</title><style>body{font-family:sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;color:#fff}*{margin:0;padding:0;box-sizing:border-box}.title{font-size:1.5rem;font-weight:700;background:linear-gradient(90deg,#00d9ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px;text-align:center}.score{text-align:center;margin:5px;font-size:1rem;color:#0f8}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;background:rgba(255,255,255,0.1);padding:8px;border-radius:10px;box-shadow:0 5px 20px rgba(0,0,0,0.3)}.cell{width:36px;height:36px;background:rgba(255,255,255,0.05);border-radius:4px;transition:0.15s}.cell.filled{box-shadow:0 0 8px currentColor}.cell.highlight{background:rgba(0,255,136,0.4)!important}.cell.invalid{background:rgba(255,0,0,0.4)!important}.cell.clearing{animation:pop 0.3s}@keyframes pop{0%{transform:scale(1)}50%{transform:scale(1.3)}100%{transform:scale(0);opacity:0}}.pieces{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap;justify-content:center}.piece{background:rgba(255,255,255,0.1);padding:5px;border-radius:8px;cursor:grab;touch-action:none}.piece-grid{display:grid;gap:1px}.piece-cell{width:18px;height:18px;border-radius:3px;box-shadow:0 0 4px currentColor}.piece-cell.empty{background:transparent}</style><div class=title>Block Blast</div><div class=score id=score>Score: 0</div><div class=grid id=grid></div><div class=pieces id=pieces></div><script>const GRID_SIZE=8;const PIECES=[{s:[1,1],c:'#FF6B6B'},{s:[1,1,1],c:'#4ECDC4'},{s:[1,1,1,1],c:'#45B7D1'},{s:[1,1,1,1,1],c:'#FFA07A'},{s:[1,1],[1,1],c:'#96CEB4'},{s:[1,1,1],[0,1,0],c:'#FFEAA7'},{s:[1,1,1],[1,0,0],c:'#D4A5A9'},{s:[1,1,1],[0,0,1],c:'#9B59B6'},{s:[1,0,0],[1,1,1],c:'#3498DB'},{s:[0,0,1],[1,1,1],c:'#E74C3C'},{s:[0,1,1],[1,1,0],c:'#2ECC71'},{s:[1,1,0],[0,1,1],c:'#F39C12'},{s:[1,0],[1,0],[1,1],c:'#1ABC9C'},{s:[0,1],[0,1],[1,1],c:'#E91E63'},{s:[1,0],[1,1],c:'#00BCD4'},{s:[0,1],[1,1],c:'#795548'}];let grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));let score=0;let pieces=[];function init(){renderGrid();spawnPieces()}function renderGrid(){const g=document.getElementById('grid');g.innerHTML='';for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){const d=document.createElement('div');d.className='cell';d.dataset.row=r;d.dataset.col=c;if(grid[r][c]){d.classList.add('filled');d.style.color=grid[r][c];d.style.background=grid[r][c]}g.appendChild(d)}}}function spawnPieces(){pieces=[];for(let i=0;i<3;i++){const idx=Math.floor(Math.random()*PIECES.length);pieces.push({...PIECES[idx],id:i})}renderPieces()}function getShape(s){if(typeof s[0]==='number')return[s.map(x=>[x])];return s}function renderPieces(){const p=document.getElementById('pieces');p.innerHTML='';pieces.forEach((pc,i)=>{const pe=document.createElement('div');pe.className='piece';const sh=getShape(pc.s);const pg=document.createElement('div');pg.className='piece-grid';pg.style.gridTemplateColumns=`repeat(${sh[0].length},1fr)`;sh.forEach(r=>{r.forEach(c=>{const d=document.createElement('div');d.className='piece-cell'+(c?'':' empty');if(c){d.style.color=pc.c;d.style.background=pc.c}pg.appendChild(d)})});pe.appendChild(pg);setupDrag(pe,i);p.appendChild(pe)})}function setupDrag(el,idx){let d;const onDown=e=>{e.preventDefault();const t=e.touches?e.touches[0]:e;d=el.cloneNode(!0);d.style.cssText='position:fixed;pointer-events:none;z-index:1000;opacity:0.8';d.style.left=t.clientX+'px';d.style.top=t.clientY+'px';document.body.appendChild(d);document.addEventListener('mousemove',onMove);document.addEventListener('mouseup',onUp);document.addEventListener('touchmove',onMove);document.addEventListener('touchend',onUp)};const onMove=e=>{if(!d)return;const t=e.touches?e.touches[0]:e;d.style.left=t.clientX+'px';d.style.top=t.clientY+'px';highlight(pieces[idx],t.clientX,t.clientY)};const onUp=e=>{if(!d)return;const t=e.changedTouches?e.changedTouches[0]:e;if(tryPlace(pieces[idx],t.clientX,t.clientY)){pieces.splice(idx,1);if(pieces.length===0)spawnPieces();checkLines()}d.remove();d=null;document.removeEventListener('mousemove',onMove);document.removeEventListener('mouseup',onUp);document.removeEventListener('touchmove',onMove);document.removeEventListener('touchend',onUp);clearHighlights()};el.addEventListener('mousedown',onDown);el.addEventListener('touchstart',onDown,{passive:!1})}function highlight(pc,x,y){clearHighlights();const g=document.getElementById('grid');const r=g.getBoundingClientRect();const c=document.querySelector('.cell').getBoundingClientRect();const px=x-r.left-8;const py=y-r.top-8;const cx=Math.floor(px/38);const cy=Math.floor(py/38);if(cx<0||cx>=GRID_SIZE||cy<0||cy>=GRID_SIZE)return;const sh=getShape(pc.s);const ro=Math.floor(sh.length/2);const co=Math.floor(sh[0].length/2);sh.forEach((rw,i)=>{rw.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;const el=document.querySelector(`.cell[data-row="${nr}"][data-col="${nc}"]`);if(el){if(nr>=0&&nr<GRID_SIZE&&nc>=0&&nc<GRID_SIZE&&!grid[nr][nc])el.classList.add('highlight');else el.classList.add('invalid')}}})})}function clearHighlights(){document.querySelectorAll('.highlight,.invalid').forEach(e=>{e.classList.remove('highlight');e.classList.remove('invalid')})}function canPlace(sh,row,col){const ro=Math.floor(sh.length/2);const co=Math.floor(sh[0].length/2);return sh.every((rw,i)=>rw.every((cell,j)=>{if(!cell)return!0;const nr=row+i-ro;const nc=col+j-co;return nr>=0&&nr<GRID_SIZE&&nc>=0&&nc<GRID_SIZE&&!grid[nr][nc]}))}function tryPlace(pc,x,y){const g=document.getElementById('grid');if(!g)return!1;const r=g.getBoundingClientRect();const c=document.querySelector('.cell').getBoundingClientRect();const px=x-r.left-8;const py=y-r.top-8;const cx=Math.floor(px/38);const cy=Math.floor(py/38);if(cx<0||cx>=GRID_SIZE||cy<0||cy>=GRID_SIZE)return!1;const sh=getShape(pc.s);if(!canPlace(sh,cx,cy))return!1;const ro=Math.floor(sh.length/2);const co=Math.floor(sh[0].length/2);sh.forEach((rw,i)=>{rw.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;grid[nr][nc]=pc.c}})});score+=countCells(sh);document.getElementById('score').textContent='Score: '+score;renderGrid();return!0}function countCells(sh){return sh.flat().filter(x=>x).length}function checkLines(){let cleared=new Set();for(let r=0;r<GRID_SIZE;r++)if(grid[r].every(c=>c!==0))for(let c=0;c<GRID_SIZE;c++)cleared.add(`${r},${c}`);for(let c=0;c<GRID_SIZE;c++)if(grid.every(r=>r[c]!==0))for(let r=0;r<GRID_SIZE;r++)cleared.add(`${r},${c}`);if(cleared.size>0){cleared.forEach(k=>{const[r,c]=k.split(',');grid[r][c]=0});score+=cleared.size*10;document.getElementById('score').textContent='Score: '+score;renderGrid()}}init();</script>"""

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    print("AP: {}".format(AP_SSID))
    print("URL: http://{}".format(AP_IP))
    return ap

def serve_page(conn):
    conn.send('HTTP/1.1 200 OK\r\n')
    conn.send('Content-Type: text/html\r\n')
    conn.send('Connection: close\r\n\r\n')
    conn.sendall(HTML)

def handle_request(conn):
    try:
        req = conn.recv(512)
        if b'GET' in req:
            serve_page(conn)
    except:
        pass
    finally:
        conn.close()

def main():
    gc.collect()
    ap = start_ap()
    addr = socket.getaddrinfo(AP_IP, 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(3)
    print("Running...")
    while True:
        try:
            conn, _ = server.accept()
            handle_request(conn)
            gc.collect()
        except:
            pass

if __name__ == "__main__":
    main()
