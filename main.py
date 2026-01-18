# Block Blast ESP32 - Main Server
# Creates AP and serves the game

try:
    import usocket as socket
except:
    import socket

import unetwork as network
import gc

# Access Point Configuration
AP_SSID = "BlockBlast"
AP_PASSWORD = "playblockblast"
AP_IP = "192.168.4.1"

# HTML Page (embedded to save memory)
HTML = """<!DOCTYPE html><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1,user-scalable=no"><title>Block Blast</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px;color:#fff}.header{text-align:center;margin-bottom:20px}.title{font-size:2rem;font-weight:700;background:linear-gradient(90deg,#00d9ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}.scores{display:flex;gap:30px;justify-content:center;flex-wrap:wrap}.score-box{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);border-radius:15px;padding:10px 20px;min-width:100px;text-align:center}.score-label{font-size:0.7rem;text-transform:uppercase;letter-spacing:1px;color:#888}.score-value{font-size:1.5rem;font-weight:700;color:#00ff88}.game-container{display:flex;flex-direction:column;align-items:center;gap:20px}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;background:rgba(255,255,255,0.1);padding:10px;border-radius:15px;box-shadow:0 10px 40px rgba(0,0,0,0.3)}.cell{width:38px;height:38px;background:rgba(255,255,255,0.05);border-radius:6px;transition:all 0.15s ease}.cell.filled{background:linear-gradient(135deg,#00d9ff,#0099ff);box-shadow:0 0 10px rgba(0,217,255,0.5)}.cell.clearing{animation:clear 0.3s ease}@keyframes clear{0%{transform:scale(1)}50%{transform:scale(1.2);background:#00ff88}100%{transform:scale(0);opacity:0}}.pieces{display:flex;gap:15px;flex-wrap:wrap;justify-content:center}.piece{background:rgba(255,255,255,0.1);padding:10px;border-radius:10px;cursor:grab;transition:transform 0.2s}.piece:hover{transform:scale(1.05)}.piece.dragging{opacity:0.5;cursor:grabbing}.piece-grid{display:grid;gap:2px}.piece-cell{width:22px;height:22px;background:linear-gradient(135deg,#ff6b6b,#ff8e53);border-radius:4px;box-shadow:0 2px 5px rgba(255,107,107,0.4)}.piece-cell.empty{background:transparent;box-shadow:none}.cell.highlight{background:rgba(0,255,136,0.3)}.btn{background:linear-gradient(135deg,#00d9ff,#0099ff);border:none;padding:12px 30px;border-radius:25px;color:#fff;font-size:1rem;font-weight:600;cursor:pointer;transition:transform 0.2s,box-shadow 0.2s;margin-top:10px}.btn:hover{transform:translateY(-2px);box-shadow:0 5px 20px rgba(0,217,255,0.4)}.btn:active{transform:translateY(0)}.game-over{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:100;opacity:0;pointer-events:none;transition:opacity 0.3s}.game-over.show{opacity:1;pointer-events:all}.game-over h2{font-size:2.5rem;margin-bottom:20px;background:linear-gradient(90deg,#ff6b6b,#ff8e53);-webkit-background-clip:text;-webkit-text-fill-color:transparent}@media (max-width:400px){.cell{width:32px;height:32px}.piece-cell{width:18px;height:18px}.title{font-size:1.5rem}}</style><div class=header><h1 class=title>Block Blast</h1><div class=scores><div class=score-box><div class=score-label>Score</div><div class=score-value id=score>0</div></div><div class=score-box><div class=score-label>Best</div><div class=score-value id=best>0</div></div></div></div><div class=game-container><div class=grid id=grid></div><div class=pieces id=pieces></div></div><div class=game-over id=gameOver><h2>Game Over!</h2><div class=score-box style=margin-bottom:20px><div class=score-label>Final Score</div><div class=score-value id=finalScore>0</div></div><button class=btn onclick=game.restart()>Play Again</button></div><script>const GRID_SIZE=8;const SHAPES=[[1,1,1,1],[1,1,1],[1,1,1],[1],[1],[1,1],[1,1],[1,1,1,1],[1,1,1,1],[1,1],[1,1,1],[1,0,1],[1,1,1],[1,1],[1,1,1],[1],[1,1,1,1],[1,1,1],[1,1],[1,1],[1,1,1],[1,1],[1,0,1,0,1],[1,1],[1,1,1],[1,1],[1,1],[1,1],[1,1]];const SHAPE_LAYOUTS=[[4,1],[3,1],[3,1],[1,1],[1,1],[2,2],[1,3],[2,2],[1,4],[1,3],[3,2],[3,1,1],[2,2],[2,2],[2,3],[2,1],[2,4],[3,1],[3,2],[1,2],[3,1],[2,1],[5,1,1],[2,2],[2,2],[2,1],[2,2],[2,2],[2,2],[1,2]];class Game{constructor(){this.grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));this.score=0;this.best=parseInt(localStorage.getItem('blockblast_best')||'0');this.pieces=[];this.init()}init(){this.renderGrid();this.spawnPieces();document.getElementById('best').textContent=this.best}renderGrid(){const gridEl=document.getElementById('grid');gridEl.innerHTML='';for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){const cell=document.createElement('div');cell.className='cell'+(this.grid[r][c]?' filled':'');cell.dataset.row=r;cell.dataset.col=c;gridEl.appendChild(cell)}}}spawnPieces(){this.pieces=[];for(let i=0;i<3;i++){const idx=Math.floor(Math.random()*SHAPES.length);this.pieces.push({shape:SHAPES[idx],layout:SHAPE_LAYOUTS[idx],id:i})}this.renderPieces()}renderPieces(){const piecesEl=document.getElementById('pieces');piecesEl.innerHTML='';for(let i=0;i<this.pieces.length;i++){const p=this.pieces[i];const pieceEl=document.createElement('div');pieceEl.className='piece';pieceEl.dataset.id=i;const gridEl=document.createElement('div');gridEl.className='piece-grid';const rows=p.layout.length;const cols=Math.max(...p.layout);gridEl.style.gridTemplateColumns=`repeat(${cols},1fr)`;for(let r=0;r<rows;r++){for(let c=0;c<p.layout[r];c++){const cell=document.createElement('div');if(r<p.layout.length&&c<p.layout[r]&&this.getShapeCell(p.shape,p.layout,r,c)){cell.className='piece-cell'}else{cell.className='piece-cell empty'}gridEl.appendChild(cell)}}pieceEl.appendChild(gridEl);this.setupPieceDrag(pieceEl,i);piecesEl.appendChild(pieceEl)}}getShapeCell(shape,layout,r,c){const idx=shape.flat().indexOf(1);if(idx===-1)return!1;const flatLayout=layout.flat();return flatLayout[r*layout[0].length+c]===1}setupPieceDrag(el,idx){let startX,startY,dragEl;const onDown=(e)=>{e.preventDefault();const touch=e.touches?e.touches[0]:e;startX=touch.clientX;startY=touch.clientY;dragEl=el.cloneNode(!0);dragEl.classList.add('dragging');dragEl.style.position='fixed';dragEl.style.pointerEvents='none';dragEl.style.zIndex='1000';document.body.appendChild(dragEl);document.addEventListener('mousemove',onMove);document.addEventListener('mouseup',onUp);document.addEventListener('touchmove',onMove);document.addEventListener('touchend',onUp)};const onMove=(e)=>{if(!dragEl)return;const touch=e.touches?e.touches[0]:e;dragEl.style.left=(touch.clientX-50)+'px';dragEl.style.top=(touch.clientY-50)+'px';this.highlightCells(this.pieces[idx],touch.clientX,touch.clientY)};const onUp=(e)=>{if(!dragEl)return;const touch=e.changedTouches?e.changedTouches[0]:e;if(this.tryPlace(this.pieces[idx],touch.clientX,touch.clientY)){this.pieces.splice(idx,1);if(this.pieces.length===0)this.spawnPieces();this.checkLines();if(!this.hasValidMoves())this.gameOver()}dragEl.remove();dragEl=null;document.removeEventListener('mousemove',onMove);document.removeEventListener('mouseup',onUp);document.removeEventListener('touchmove',onMove);document.removeEventListener('touchend',onUp);this.clearHighlights()};el.addEventListener('mousedown',onDown);el.addEventListener('touchstart',onDown,{passive:!1})}highlightCells(piece,x,y){this.clearHighlights();const pos=this.getGridPos(x,y);if(!pos)return;for(let r=0;r<piece.layout.length;r++){for(let c=0;c<piece.layout[r];c++){const cell=document.querySelector(`.cell[data-row="${pos.r+r}"][data-col="${pos.c+c}"]`);if(cell&&this.canPlaceAt(piece,pos.r,pos.c))cell.classList.add('highlight')}}}clearHighlights(){document.querySelectorAll('.cell.highlight').forEach(el=>el.classList.remove('highlight'))}getGridPos(x,y){const cell=document.querySelector('.cell');if(!cell)return null;const rect=cell.getBoundingClientRect();return{r:Math.floor((y-rect.top)/rect.height)-3,c:Math.floor((x-rect.left)/rect.width)-4}}canPlaceAt(piece,row,col){for(let r=0;r<piece.layout.length;r++){for(let c=0;c<piece.layout[r];c++){const nr=row+r,nc=col+c;if(nr<0||nr>=GRID_SIZE||nc<0||nc>=GRID_SIZE||this.grid[nr][nc])return!1}}return!0}tryPlace(piece,x,y){const pos=this.getGridPos(x,y);if(!pos||!this.canPlaceAt(piece,pos.r,pos.c))return!1;for(let r=0;r<piece.layout.length;r++){for(let c=0;c<piece.layout[r];c++){this.grid[pos.r+r][pos.c+c]=1}}this.score+=this.countCells(piece);this.updateScore();this.renderGrid();return!0}countCells(piece){return piece.layout.reduce((a,r)=>a+r,0)}checkLines(){let lines=[];for(let r=0;r<GRID_SIZE;r++){if(this.grid[r].every(c=>c))lines.push(this.grid[r])}for(let c=0;c<GRID_SIZE;c++){if(this.grid.every(row=>row[c]))lines.push(this.grid.map(row=>row[c]))}if(lines.length>0){this.animateClear(lines);this.score+=lines.length*10*GRID_SIZE;this.updateScore();setTimeout(()=>this.clearLines(lines),300)}}animateClear(lines){lines.forEach(line=>{for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){if(line===this.grid[r]||line.includes(this.grid[r][c])){const cell=document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);if(cell)cell.classList.add('clearing')}}}})}clearLines(lines){for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){if(this.grid[r][c]&&(lines.includes(this.grid[r])||lines.some(l=>l.includes(this.grid[r][c])))){this.grid[r][c]=0}}}this.renderGrid()}hasValidMoves(){for(let p of this.pieces){for(let r=0;r<GRID_SIZE;r++){for(let c=0;c<GRID_SIZE;c++){if(this.canPlaceAt(p,r,c))return!0}}}return!1}updateScore(){document.getElementById('score').textContent=this.score;if(this.score>this.best){this.best=this.score;localStorage.setItem('blockblast_best',this.best);document.getElementById('best').textContent=this.best}}gameOver(){document.getElementById('finalScore').textContent=this.score;document.getElementById('gameOver').classList.add('show')}restart(){this.grid=Array(GRID_SIZE).fill(null).map(()=>Array(GRID_SIZE).fill(0));this.score=0;this.updateScore();document.getElementById('gameOver').classList.remove('show');this.spawnPieces()}}const game=new Game();</script>"""

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
    # Free memory before starting
    gc.collect()

    # Start AP
    ap = start_ap()

    # Start server
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
