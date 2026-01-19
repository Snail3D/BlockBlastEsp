# Block Blast ESP32 - Main Server
try:
    import usocket as socket
except:
    import socket
import network
import gc

AP_SSID = "BlockBlast"
AP_PASSWORD = "playblockblast"
AP_IP = "192.168.4.1"

HTML = """<!DOCTYPE html><html><head><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Blast</title><style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a1a2e;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:10px;color:#fff;font-family:sans-serif}.title{font-size:1.6rem;font-weight:700;background:linear-gradient(90deg,#0cf,#0f8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}.score{font-size:1.1rem;color:#0f8;margin-bottom:10px}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;background:#2a2a4e;padding:8px;border-radius:8px;box-shadow:0 5px 20px rgba(0,0,0,0.4)}.cell{width:36px;height:36px;background:#3a3a5e;border-radius:4px}.cell.filled{box-shadow:0 0 8px currentColor}.cell.hl{background:#0f8!important;box-shadow:0 0 12px #0f8}.cell.inv{background:#f44!important;box-shadow:0 0 12px #f44}.pieces{display:flex;gap:10px;margin-top:15px;flex-wrap:wrap;justify-content:center}.piece{background:#2a2a4e;padding:8px;border-radius:6px;cursor:grab;border:1px solid #4a4a7e}.piece:hover{border-color:#0cf;box-shadow:0 0 10px rgba(0,204,255,0.3)}.piece-grid{display:grid;gap:1px}.piece-cell{width:16px;height:16px;border-radius:3px;box-shadow:0 0 4px currentColor}.piece-cell.e{background:transparent}</style></head><body><div class=title>Block Blast</div><div class=score id=score>Score: 0</div><div class=grid id=grid></div><div class=pieces id=pieces></div><script>const S=8;const P=[{s:[1,1],c:'#F66'},{s:[1,1,1],c:'#4CD'},{s:[1,1,1,1],c:'#4B7'},{s:[1,1,1,1,1],c:'#FA7'},{s:[1,1],[1,1],c:'#9CE'},{s:[1,1,1],[0,1,0],c:'#FE7'},{s:[1,1,1],[1,0,0],c:'#D75'},{s:[1,1,1],[0,0,1],c:'#959'},{s:[1,0,0],[1,1,1],c:'#38D'},{s:[0,0,1],[1,1,1],c:'#F43'},{s:[0,1,1],[1,1,0],c:'#2E7'},{s:[1,1,0],[0,1,1],c:'#F92'},{s:[1,0],[1,0],[1,1],c:'#1AC'},{s:[0,1],[0,1],[1,1],c:'#E91'},{s:[1,0],[1,1],c:'#0BC'},{s:[0,1],[1,1],c:'#754'}];let g=Array(S).fill(null).map(()=>Array(S).fill(0));let sc=0;let ps=[];function init(){R();spawn()}function R(){const gr=document.getElementById('grid');gr.innerHTML='';for(let r=0;r<S;r++){for(let c=0;c<S;c++){const d=document.createElement('div');d.className='cell';d.dataset.r=r;d.dataset.c=c;if(g[r][c]){d.classList.add('filled');d.style.color=g[r][c];d.style.background=g[r][c]}gr.appendChild(d)}}}function spawn(){ps=[];for(let i=0;i<3;i++){const idx=Math.floor(Math.random()*P.length);ps.push({...P[idx],id:i})}rend()}function sh(s){return typeof s[0]==='number'?s.map(x=>[x]):s}function rend(){const p=document.getElementById('pieces');p.innerHTML='';ps.forEach((pc,i)=>{const pe=document.createElement('div');pe.className='piece';const s=sh(pc.s);const pg=document.createElement('div');pg.className='piece-grid';pg.style.gridTemplateColumns=`repeat(${s[0].length},1fr)`;s.forEach(r=>{r.forEach(c=>{const d=document.createElement('div');d.className='piece-cell'+(c?'':' e');if(c){d.style.color=pc.c;d.style.background=pc.c}pg.appendChild(d)})});pe.appendChild(pg);drag(pe,i);p.appendChild(pe)})}function drag(el,i){let d;const onDown=e=>{e.preventDefault();const t=e.touches?e.touches[0]:e;d=el.cloneNode(!0);d.style.cssText='position:fixed;pointer-events:none;z-index:1000;opacity:0.85';d.style.left=(t.clientX-25)+'px';d.style.top=(t.clientY-25)+'px';document.body.appendChild(d);document.addEventListener('mousemove',onMove);document.addEventListener('mouseup',onUp);document.addEventListener('touchmove',onMove);document.addEventListener('touchend',onUp)};const onMove=e=>{if(!d)return;const t=e.touches?e.touches[0]:e;d.style.left=(t.clientX-25)+'px';d.style.top=(t.clientY-25)+'px';hl(ps[i],t.clientX,t.clientY)};const onUp=e=>{if(!d)return;const t=e.changedTouches?e.changedTouches[0]:e;if(place(ps[i],t.clientX,t.clientY)){ps.splice(i,1);if(ps.length===0)spawn();chk()}d.remove();d=null;document.removeEventListener('mousemove',onMove);document.removeEventListener('mouseup',onUp);document.removeEventListener('touchmove',onMove);document.removeEventListener('touchend',onUp);clr()};el.addEventListener('mousedown',onDown);el.addEventListener('touchstart',onDown,{passive:!1})}function hl(pc,x,y){clr();const gr=document.getElementById('grid');const rc=gr.getBoundingClientRect();const cl=document.querySelector('.cell');if(!cl)return;const cc=cl.getBoundingClientRect();const px=x-rc.left-8;const py=y-rc.top-8;const cx=Math.floor(px/(cc.width+2));const cy=Math.floor(py/(cc.height+2));if(cx<0||cx>=S||cy<0||cy>=S)return;const s=sh(pc.s);const ro=Math.floor(s.length/2);const co=Math.floor(s[0].length/2);s.forEach((rw,i)=>{rw.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;const el=document.querySelector(`.cell[data-r="${nr}"][data-c="${nc}"]`);if(el){if(nr>=0&&nr<S&&nc>=0&&nc<S&&!g[nr][nc])el.classList.add('hl');else el.classList.add('inv')}}})})}function clr(){document.querySelectorAll('.hl,.inv').forEach(e=>{e.classList.remove('hl');e.classList.remove('inv')})}function can(s,r,c){const ro=Math.floor(s.length/2);const co=Math.floor(s[0].length/2);return s.every((rw,i)=>rw.every((cell,j)=>{if(!cell)return!0;const nr=r+i-ro;const nc=c+j-co;return nr>=0&&nr<S&&nc>=0&&nc<S&&!g[nr][nc]}))}function place(pc,x,y){const gr=document.getElementById('grid');if(!gr)return!1;const rc=gr.getBoundingClientRect();const cl=document.querySelector('.cell');if(!cl)return!1;const cc=cl.getBoundingClientRect();const px=x-rc.left-8;const py=y-rc.top-8;const cx=Math.floor(px/(cc.width+2));const cy=Math.floor(py/(cc.height+2));if(cx<0||cx>=S||cy<0||cy>=S)return!1;const s=sh(pc.s);if(!can(s,cx,cy))return!1;const ro=Math.floor(s.length/2);const co=Math.floor(s[0].length/2);s.forEach((rw,i)=>{rw.forEach((cell,j)=>{if(cell){const nr=cy+i-ro;const nc=cx+j-co;g[nr][nc]=pc.c}})});sc+=s.flat().filter(x=>x).length;document.getElementById('score').textContent='Score: '+sc;R();return!0}function chk(){let cl=new Set();for(let r=0;r<S;r++)if(g[r].every(c=>c!==0))for(let c=0;c<S;c++)cl.add(`${r},${c}`);for(let c=0;c<S;c++)if(g.every(r=>r[c]!==0))for(let r=0;r<S;r++)cl.add(`${r},${c}`);if(cl.size>0){cl.forEach(k=>{const[r,c]=k.split(',');g[r][c]=0});sc+=cl.size*10;document.getElementById('score').textContent='Score: '+sc;R()}}init();</script></body></html>"""

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
