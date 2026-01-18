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

# Simplified HTML for ESP32 memory constraints
HTML = """<!DOCTYPE html><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Blast</title><style>body{font-family:sans-serif;background:#1a1a2e;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;color:#fff}*{margin:0;padding:0;box-sizing:border-box}.title{font-size:1.5rem;font-weight:700;color:#00d9ff;margin-bottom:10px;text-align:center}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:1px;background:#333;padding:5px}.cell{width:36px;height:36px;background:#444}.cell.filled{background:#00d9ff}.cell.highlight{background:#0f0}.cell.invalid{background:#f00}.pieces{display:flex;gap:10px;margin-top:20px;flex-wrap:wrap;justify-content:center}.piece{background:#333;padding:5px;cursor:grab}.piece-grid{display:grid;gap:1px}.piece-cell{width:18px;height:18px;background:#f64}.piece-cell.empty{background:transparent}.score{text-align:center;margin:10px;font-size:1.2rem;color:#0f8}</style><div class=title>Block Blast</div><div class=score id=score>Score: 0</div><div class=grid id=grid></div><div class=pieces id=pieces></div><script>const GRID_SIZE=8;const PIECES=[[1,1],[1,1,1],[1,1,1,1],[1,1,1,1,1],[1,1],[1,1],[1,1],[1,1,1],[1,1,1],[1,0,1],[1,1,1],[1,0,0,1],[1,0],[1,0,1,1],[0,1,1],[1,1,0],[1,0,1],[1,0,0,1],[1,1],[0,1],[1,1,0],[0,1,1],[1,1,1],[1,1,1],[0,1,0]];const COLORS=["#00d9ff","#4db6ac","#ff8a65","#fff176","#ba68c8","#e57373"];let grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));let score=0;let pieces=[];function init(){renderGrid();spawnPieces()}function renderGrid(){const g=document.getElementById('grid');g.innerHTML='';for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){const d=document.createElement('div');d.className='cell'+(grid[r][c]?' filled':'');d.dataset.row=r;d.dataset.col=c;g.appendChild(d)}}}function spawnPieces(){pieces=[];for(let i=0;i<3;i++){const idx=Math.floor(Math.random()*PIECES.length);pieces.push({shape:PIECES[idx],color:COLORS[idx%COLORS.length]})}renderPieces()}function getPieceShape(s){if(s.length===1)return[[s[0]]];if(s[0]===1&&s[1]===1)return[[1,1]];if(s[0]===1&&s[1]===0)return[[1,0]];if(s[0]===0&&s[1]===1)return[[0,1]];if(s.length===2)return[[s[0]],[s[1]]];if(s.length===3){if(s[1]===0)return[[1,0,0],[1,1,1]];if(s[2]===0)return[[1,1,1],[1,0,0]];if(s[1]===1)return[[1,1,1],[0,1,0]];return[[s[0]],[s[1]],[s[2]]]};if(s.length===4){if(s[1]===0&&s[2]===0)return[[1,0,0,0],[1,1,1,1]];if(s[1]===0&&s[3]===0)return[[1,0,0,0],[0,0,1,0],[1,0,0,0],[0,0,1,0]];if(s[1]===1&&s[3]===0)return[[1,1,1,1],[0,0,1,0]];if(s[2]===1&&s[3]===0)return[[1,1,1,1],[0,0,0,1]];if(s[1]===1&&s[2]===0)return[[1,1,1,1],[0,1,0]];if(s[2]===1)return[[s[0]],[s[1]],[s[2]],[s[3]]];return[[s[0],s[1],s[2],s[3]]]};if(s.length===5)return[[s[0]],[s[1]],[s[2]],[s[3]],[s[4]]];return[[s[0]]]}function renderPieces(){const p=document.getElementById('pieces');p.innerHTML='';pieces.forEach((pc,i)=>{const pe=document.createElement('div');pe.className='piece';const shape=getPieceShape(pc.shape);const pg=document.createElement('div');pg.className='piece-grid';const cols=shape[0].length;pg.style.gridTemplateColumns=`repeat(${cols},1fr)`;shape.forEach(row=>{row.forEach(cell=>{const c=document.createElement('div');c.className='piece-cell'+(cell?'':' empty');if(cell)c.style.background=pc.color;pg.appendChild(c)})});pe.appendChild(pg);setupDrag(pe,i);p.appendChild(pe)})}function setupDrag(el,idx){let d;const onDown=e=>{e.preventDefault();const t=e.touches?e.touches[0]:e;d=el.cloneNode(!0);d.style.cssText='position:fixed;pointer-events:none;z-index:1000;opacity:0.7';d.style.left=t.clientX+'px';d.style.top=t.clientY+'px';document.body.appendChild(d);document.addEventListener('mousemove',onMove);document.addEventListener('mouseup',onUp);document.addEventListener('touchmove',onMove);document.addEventListener('touchend',onUp)};const onMove=e=>{if(!d)return;const t=e.touches?e.touches[0]:e;d.style.left=t.clientX+'px';d.style.top=t.clientY+'px';highlight(pieces[idx],t.clientX,t.clientY)};const onUp=e=>{if(!d)return;const t=e.changedTouches?e.changedTouches[0]:e;tryPlace(pieces[idx],t.clientX,t.clientY);d.remove();d=null;document.removeEventListener('mousemove',onMove);document.removeEventListener('mouseup',onUp);document.removeEventListener('touchmove',onMove);document.removeEventListener('touchend',onUp);clearHighlights()};el.addEventListener('mousedown',onDown);el.addEventListener('touchstart',onDown,{passive:!1})}function highlight(pc,x,y){clearHighlights();const g=document.getElementById('grid');const r=g.getBoundingClientRect();const c=document.querySelector('.cell').getBoundingClientRect();const px=x-r.left-5;const py=y-r.top-5;const cx=Math.floor(px/37);const cy=Math.floor(py/37);if(cx<0||cx>=GRID_SIZE||cy<0||cy>=GRID_SIZE)return;const shape=getPieceShape(pc.shape);const ro=Math.floor(shape.length/2);const co=Math.floor(shape[0].length/2);shape.forEach((row,i)=>{row.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;const el=document.querySelector(`.cell[data-row="${nr}"][data-col="${nc}"]`);if(el){if(nr>=0&&nr<GRID_SIZE&&nc>=0&&nc<GRID_SIZE&&!grid[nr][nc])el.classList.add('highlight');else el.classList.add('invalid')}}})})}function clearHighlights(){document.querySelectorAll('.highlight,.invalid').forEach(e=>{e.classList.remove('highlight');e.classList.remove('invalid')})}function canPlace(shape,row,col){const ro=Math.floor(shape.length/2);const co=Math.floor(shape[0].length/2);return shape.every((rw,i)=>rw.every((cell,j)=>{if(!cell)return!0;const nr=row+i-ro;const nc=col+j-co;return nr>=0&&nr<GRID_SIZE&&nc>=0&&nc<GRID_SIZE&&!grid[nr][nc]}))}function tryPlace(pc,x,y){const g=document.getElementById('grid');if(!g)return!1;const r=g.getBoundingClientRect();const c=document.querySelector('.cell').getBoundingClientRect();const px=x-r.left-5;const py=y-r.top-5;const cx=Math.floor(px/37);const cy=Math.floor(py/37);if(cx<0||cx>=GRID_SIZE||cy<0||cy>=GRID_SIZE)return!1;const shape=getPieceShape(pc.shape);if(!canPlace(shape,cx,cy))return!1;const ro=Math.floor(shape.length/2);const co=Math.floor(shape[0].length/2);shape.forEach((rw,i)=>{rw.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;grid[nr][nc]=pc.color}})});score+=countCells(pc);document.getElementById('score').textContent='Score: '+score;renderGrid();if(pieces.length<=1)spawnPieces();return!0}function countCells(pc){return getPieceShape(pc.shape).flat().filter(x=>x).length}init();</script>"""

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
