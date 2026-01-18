# Block Blast ESP32 - Main Server
# Creates AP and serves the game

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

# HTML Page (minified for ESP32 memory)
HTML = """<!DOCTYPE html><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1,user-scalable=no"><title>Block Blast</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;color:#fff;user-select:none}.title{font-size:2rem;font-weight:700;background:linear-gradient(90deg,#00d9ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}.scores{display:flex;gap:30px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}.score-box{background:rgba(255,255,255,0.1);border-radius:15px;padding:10px 20px;min-width:100px;text-align:center}.score-label{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;color:#888}.score-value{font-size:1.5rem;font-weight:700;color:#00ff88}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;background:rgba(255,255,255,0.1);padding:10px;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.3);margin-bottom:20px}.cell{width:38px;height:38px;background:rgba(255,255,255,0.05);border-radius:6px}.cell.filled{background:linear-gradient(135deg,#00d9ff,#0099ff);box-shadow:0 0 10px rgba(0,217,255,0.5)}.cell.highlight{background:rgba(0,255,136,0.4)!important;box-shadow:0 0 15px rgba(0,255,136,0.6)}.cell.invalid{background:rgba(255,50,50,0.4)!important}.pieces{display:flex;gap:15px;flex-wrap:wrap;justify-content:center}.piece{background:rgba(255,255,255,0.1);padding:10px;border-radius:10px;cursor:grab;touch-action:none}.piece-grid{display:grid;gap:2px}.piece-cell{width:22px;height:22px;border-radius:4px;box-shadow:0 2px 5px rgba(255,107,107,0.4)}.piece-cell.empty{background:transparent;box-shadow:none}.btn{background:linear-gradient(135deg,#00d9ff,#0099ff);border:none;padding:12px 30px;border-radius:25px;color:#fff;font-size:1rem;font-weight:600;cursor:pointer;margin-top:10px}.game-over{position:fixed;top:0;left:0;right;0;bottom:0;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:100;opacity:0;pointer-events:none}.game-over.show{opacity:1;pointer-events:all}.game-over h2{font-size:2.5rem;margin-bottom:20px;background:linear-gradient(90deg,#ff6b6b,#ff8e53);-webkit-background-clip:text;-webkit-text-fill-color:transparent}@media(max-width:400px){.cell{width:32px;height:32px}.piece-cell{width:18px;height:18px}.title{font-size:1.5rem}}</style><h1 class=title>Block Blast</h1><div class=scores><div class=score-box><div class=score-label>Score</div><div class=score-value id=score>0</div></div><div class=score-box><div class=score-label>Best</div><div class=score-value id=best>0</div></div></div><div class=grid id=grid></div><div class=pieces id=pieces></div><div class=game-over id=gameOver><h2>Game Over!</h2><div class=score-box style=margin-bottom:20px><div class=score-label>Final Score</div><div class=score-value id=finalScore>0</div></div><button class=btn onclick=game.restart()>Play Again</button></div><script>const GRID_SIZE=8;const PIECES=[{shape:[[1,1]],color:'#4FC3F7'},{shape:[[1],[1]],color:'#4FC3F7'},{shape:[[1,1,1]],color:'#81C784'},{shape:[[1],[1],[1]],color:'#81C784'},{shape:[[1,1,1,1]],color:'#64B5F6'},{shape:[[1],[1],[1],[1]],color:'#64B5F6'},{shape:[[1,1],[1,1]],color:'#FFF176'},{shape:[[1,1,1],[0,1,0]],color:'#BA68C8'},{shape:[[1,1,1],[1,0,0]],color:'#FF8A65'},{shape:[[1,1,1],[0,0,1]],color:'#4DB6AC'},{shape:[[1,0,0],[1,1,1]],color:'#7986CB'},{shape:[[0,0,1],[1,1,1]],color:'#9575CD'},{shape:[[0,1,1],[1,1,0]],color:'#AED581'},{shape:[[1,1,0],[0,1,1]],color:'#F06292'},{shape:[[1,0],[1,0],[1,1]],color:'#E57373'},{shape:[[0,1],[0,1],[1,1]],color:'#64B5F6'},{shape:[[1,0],[1,1]],color:'#FFB74D'},{shape:[[0,1],[1,1]],color:'#4DB6AC'},{shape:[[1,1,1],[0,1,0]],color:'#BA68C8'},{shape:[[1,1,1,1,1]],color:'#90A4AE'},{shape:[[1],[1],[1],[1],[1]],color:'#90A4AE'}];class Game{constructor(){this.grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));this.score=0;this.best=parseInt(localStorage.getItem('blockblast_best')||'0');this.pieces=[];this.init()}init(){this.renderGrid();this.spawnPieces();document.getElementById('best').textContent=this.best}renderGrid(){const gridEl=document.getElementById('grid');gridEl.innerHTML='';for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){const cell=document.createElement('div');cell.className='cell'+(this.grid[r][c]?' filled':'');cell.dataset.row=r;cell.dataset.col=c;gridEl.appendChild(cell)}}}spawnPieces(){this.pieces=[];for(let i=0;i<3;i++){const idx=Math.floor(Math.random()*PIECES.length);this.pieces.push({...PIECES[idx],id:i})}this.renderPieces()}renderPieces(){const piecesEl=document.getElementById('pieces');piecesEl.innerHTML='';for(let i=0;i<this.pieces.length;i++){const p=this.pieces[i];const pieceEl=document.createElement('div');pieceEl.className='piece';pieceEl.dataset.id=i;const gridEl=document.createElement('div');gridEl.className='piece-grid';gridEl.style.gridTemplateColumns=`repeat(${p.shape[0].length},1fr)`;for(let r=0;r<p.shape.length;r++){for(let c=0;c<p.shape[r].length;c++){const cell=document.createElement('div');if(p.shape[r][c]){cell.className='piece-cell';cell.style.background=`linear-gradient(135deg,${p.color},${this.adjustColor(p.color,-20)})`}else{cell.className='piece-cell empty'}gridEl.appendChild(cell)}}pieceEl.appendChild(gridEl);this.setupPieceDrag(pieceEl,i);piecesEl.appendChild(pieceEl)}}adjustColor(hex,amount){const num=parseInt(hex.slice(1),16);const r=Math.min(255,Math.max(0,(num>>16)+amount));const g=Math.min(255,Math.max(0,((num>>8)&0x00FF)+amount));const b=Math.min(255,Math.max(0,(num&0x0000FF)+amount));return'#'+((r<<16)|(g<<8)|b).toString(16).padStart(6,'0')}setupPieceDrag(el,idx){let dragEl;const onDown=(e)=>{e.preventDefault();const touch=e.touches?e.touches[0]:e;dragEl=el.cloneNode(!0);dragEl.style.position='fixed';dragEl.style.pointerEvents='none';dragEl.style.zIndex='1000';dragEl.style.opacity='0.8';dragEl.style.left=touch.clientX+'px';dragEl.style.top=touch.clientY+'px';document.body.appendChild(dragEl);document.addEventListener('mousemove',onMove);document.addEventListener('mouseup',onUp);document.addEventListener('touchmove',onMove);document.addEventListener('touchend',onUp)};const onMove=(e)=>{if(!dragEl)return;const touch=e.touches?e.touches[0]:e;dragEl.style.left=touch.clientX+'px';dragEl.style.top=touch.clientY+'px';this.highlightCells(this.pieces[idx],touch.clientX,touch.clientY)};const onUp=(e)=>{if(!dragEl)return;const touch=e.changedTouches?e.changedTouches[0]:e;const placed=this.tryPlace(this.pieces[idx],touch.clientX,touch.clientY);dragEl.remove();dragEl=null;document.removeEventListener('mousemove',onMove);document.removeEventListener('mouseup',onUp);document.removeEventListener('touchmove',onMove);document.removeEventListener('touchend',onUp);this.clearHighlights();if(placed){this.pieces.splice(idx,1);if(this.pieces.length===0)this.spawnPieces();this.checkLines();if(!this.hasValidMoves())this.gameOver()}};el.addEventListener('mousedown',onDown);el.addEventListener('touchstart',onDown,{passive:!1})}highlightCells(piece,x,y){this.clearHighlights();const gridEl=document.getElementById('grid');if(!gridEl)return;const rect=gridEl.getBoundingClientRect();const cellEl=document.querySelector('.cell');if(!cellEl)return;const cellRect=cellEl.getBoundingClientRect();const cellW=cellRect.width;const cellH=cellRect.height;const padding=10;const relX=x-rect.left-padding;const relY=y-rect.top-padding;if(relX<-cellW/2||relY<-cellH/2)return;const centerC=Math.floor((relX+cellW/2)/cellW);const centerR=Math.floor((relY+cellH/2)/cellH);if(centerR<0||centerR>=GRID_SIZE||centerC<0||centerC>=GRID_SIZE)return;for(let r=0;r<piece.shape.length;r++){for(let c=0;c<piece.shape[r].length;c++){if(piece.shape[r][c]){const nr=centerR+r-Math.floor(piece.shape.length/2);const nc=centerC+c-Math.floor(piece.shape[0].length/2);const cell=document.querySelector(`.cell[data-row="${nr}"][data-col="${nc}"]`);if(cell){if(nr>=0&&nr<GRID_SIZE&&nc>=0&&nc<GRID_SIZE&&!this.grid[nr][nc]){cell.classList.add('highlight')}else{cell.classList.add('invalid')}}}}}}clearHighlights(){document.querySelectorAll('.cell.highlight, .cell.invalid').forEach(el=>{el.classList.remove('highlight');el.classList.remove('invalid')})}canPlaceAt(piece,row,col){for(let r=0;r<piece.shape.length;r++){for(let c=0;c<piece.shape[r].length;c++){if(!piece.shape[r][c])continue;const nr=row+r-Math.floor(piece.shape.length/2);const nc=col+c-Math.floor(piece.shape[0].length/2);if(nr<0||nr>=GRID_SIZE||nc<0||nc>=GRID_SIZE||this.grid[nr][nc])return false}return true}}tryPlace(piece,x,y){const gridEl=document.getElementById('grid');if(!gridEl)return false;const rect=gridEl.getBoundingClientRect();const cellEl=document.querySelector('.cell');if(!cellEl)return false;const cellRect=cellEl.getBoundingClientRect();const cellW=cellRect.width;const cellH=cellRect.height;const padding=10;const relX=x-rect.left-padding;const relY=y-rect.top-padding;if(relX<-cellW/2||relY<-cellH/2)return false;const centerC=Math.floor((relX+cellW/2)/cellW);const centerR=Math.floor((relY+cellH/2)/cellH);if(centerR<0||centerR>=GRID_SIZE||centerC<0||centerC>=GRID_SIZE)return false;if(!this.canPlaceAt(piece,centerR,centerC))return false;for(let r=0;r<piece.shape.length;r++){for(let c=0;c<piece.shape[r].length;c++){if(piece.shape[r][c]){const nr=centerR+r-Math.floor(piece.shape.length/2);const nc=centerC+c-Math.floor(piece.shape[0].length/2);this.grid[nr][nc]=piece.color}}}this.score+=this.countCells(piece);this.updateScore();this.renderGrid();return true}countCells(piece){return piece.shape.flat().filter(x=>x).length}checkLines(){let lines=[];for(let r=0;r<GRID_SIZE;r++)if(this.grid[r].every(c=>c!==0))lines.push(this.grid[r]);for(let c=0;c<GRID_SIZE;c++)if(this.grid.every(row=>row[c]!==0))lines.push(this.grid.map(row=>row[c]));if(lines.length>0){this.score+=lines.length*10*GRID_SIZE;this.updateScore();setTimeout(()=>this.clearLines(lines),200)}}clearLines(lines){const toClear=new Set;lines.forEach(line=>{for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){if(line===this.grid[r])toClear.add(`${r},${c}`);else if(Array.isArray(line)&&this.grid[r][c]===line[c]&&line[c]!==0)toClear.add(`${r},${c}`)}}});toClear.forEach(key=>{const[r,c]=key.split(',').map(Number);this.grid[r][c]=0});this.renderGrid()}hasValidMoves(){for(let p of this.pieces){for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){if(this.canPlaceAt(p,r,c))return true}}return false}updateScore(){document.getElementById('score').textContent=this.score;if(this.score>this.best){this.best=this.score;localStorage.setItem('blockblast_best',this.best);document.getElementById('best').textContent=this.best}}gameOver(){document.getElementById('finalScore').textContent=this.score;document.getElementById('gameOver').classList.add('show')}restart(){this.grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));this.score=0;this.updateScore();document.getElementById('gameOver').classList.remove('show');this.spawnPieces()}}const game=new Game();</script>"""

def start_ap():
    """Start the WiFi Access Point"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    print("AP started: {}".format(AP_SSID))
    print("Connect to http://{}".format(AP_IP))
    return ap

def serve_page(conn):
    """Serve the game HTML page"""
    conn.send('HTTP/1.1 200 OK\r\n')
    conn.send('Content-Type: text/html\r\n')
    conn.send('Connection: close\r\n\r\n')
    conn.sendall(HTML)

def handle_request(conn):
    """Handle incoming HTTP request"""
    try:
        request = conn.recv(1024).decode()
        if 'GET' in request:
            serve_page(conn)
    except:
        pass
    finally:
        conn.close()

def main():
    """Main server loop"""
    gc.collect()
    ap = start_ap()
    addr = socket.getaddrinfo(AP_IP, 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(5)
    print("Server running on http://{}".format(AP_IP))

    while True:
        try:
            conn, _ = server.accept()
            handle_request(conn)
        except Exception as e:
            print("Error: {}".format(e))
            gc.collect()

if __name__ == "__main__":
    main()
