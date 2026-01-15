// Block Blast - ESP32 Version
// Game Constants
const GRID_SIZE = 8;
const CELL_SIZE = 40;
const CANVAS_SIZE = GRID_SIZE * CELL_SIZE;
const PIECE_CELL_SIZE = 20;

// Block Blast colors
const COLORS = {
    cyan: '#00d4aa',
    blue: '#00a8cc',
    orange: '#ff8c42',
    yellow: '#ffdd00',
    green: '#7ec850',
    red: '#ff5252',
    purple: '#a855f7',
    pink: '#ff6b9d',
    empty: '#1e293b',
    grid: '#334155'
};

const COLOR_KEYS = Object.keys(COLORS).filter(k => k !== 'empty' && k !== 'grid');

// Piece shapes (Tetris-like polyominoes)
const PIECES = [
    // Single
    { shape: [[1]], color: 'cyan' },
    // 2-block line
    { shape: [[1, 1]], color: 'blue' },
    { shape: [[1], [1]], color: 'blue' },
    // 3-block line
    { shape: [[1, 1, 1]], color: 'green' },
    { shape: [[1], [1], [1]], color: 'green' },
    // 4-block line
    { shape: [[1, 1, 1, 1]], color: 'orange' },
    { shape: [[1], [1], [1], [1]], color: 'orange' },
    // 2x2 square
    { shape: [[1, 1], [1, 1]], color: 'yellow' },
    // L shapes
    { shape: [[1, 0], [1, 0], [1, 1]], color: 'red' },
    { shape: [[1, 1, 1], [1, 0, 0]], color: 'red' },
    { shape: [[0, 1], [0, 1], [1, 1]], color: 'purple' },
    { shape: [[1, 0, 0], [1, 1, 1]], color: 'purple' },
    { shape: [[1, 1], [0, 1], [0, 1]], color: 'pink' },
    { shape: [[0, 0, 1], [1, 1, 1]], color: 'pink' },
    { shape: [[1, 1], [1, 0], [1, 0]], color: 'cyan' },
    { shape: [[1, 1, 1], [0, 0, 1]], color: 'cyan' },
    // T shape
    { shape: [[1, 1, 1], [0, 1, 0]], color: 'blue' },
    { shape: [[0, 1], [1, 1], [0, 1]], color: 'blue' },
    // Z/S shapes
    { shape: [[1, 1, 0], [0, 1, 1]], color: 'green' },
    { shape: [[0, 1], [1, 1], [1, 0]], color: 'green' },
    { shape: [[0, 1, 1], [1, 1, 0]], color: 'orange' },
    { shape: [[1, 0], [1, 1], [0, 1]], color: 'orange' },
    // 5-block shapes
    { shape: [[1, 1, 1, 1, 1]], color: 'red' },
    { shape: [[1], [1], [1], [1], [1]], color: 'red' },
    { shape: [[1, 1, 1], [1, 1, 0]], color: 'purple' },
    { shape: [[1, 1, 1], [0, 1, 1]], color: 'purple' },
    { shape: [[1, 1], [1, 1], [1, 0]], color: 'yellow' },
    { shape: [[1, 1], [1, 1], [0, 1]], color: 'yellow' },
    // Cross/plus
    { shape: [[0, 1, 0], [1, 1, 1]], color: 'pink' },
    { shape: [[1, 0], [1, 1], [1, 0]], color: 'pink' }
];

// Block Blast scoring: 10 points per block cleared
// Combo bonus: 1 line = +20, 2 lines = +30, 3 lines = +40, ..., 9 lines = +100
const POINTS_PER_BLOCK = 10;
const COMBO_BONUS = [0, 20, 30, 40, 50, 60, 70, 80, 90, 100];

// Game state
let grid = [];
let score = 0;
let highScore = parseInt(localStorage.getItem('blockBlastHighScore')) || 0;
let currentPieces = [];
let pieceCanvases = [];
let draggedPiece = null;
let draggedPieceIndex = -1;
let ghostPosition = null; // {row, col, valid}
let streakCount = 0; // Consecutive placements that cleared lines

// Canvas setup
const gameCanvas = document.getElementById('gameCanvas');
const ctx = gameCanvas.getContext('2d');

// Initialize game
function init() {
    // Initialize grid
    grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(null));

    // Update high score display
    document.getElementById('highScore').textContent = highScore;

    // Generate initial pieces
    generateNewPieces();

    // Draw initial grid
    drawGrid();

    // Setup event listeners
    setupEventListeners();
}

function generateNewPieces() {
    currentPieces = [];
    for (let i = 0; i < 3; i++) {
        const randomPiece = PIECES[Math.floor(Math.random() * PIECES.length)];
        currentPieces.push(JSON.parse(JSON.stringify(randomPiece)));
    }
    renderPieces();
}

function renderPieces() {
    const slots = ['piece0', 'piece1', 'piece2'];

    slots.forEach((slotId, index) => {
        const slot = document.getElementById(slotId);
        slot.innerHTML = '';

        if (currentPieces[index]) {
            const piece = currentPieces[index];
            const shape = piece.shape;
            const rows = shape.length;
            const cols = shape[0].length;

            const canvas = document.createElement('canvas');
            canvas.width = cols * PIECE_CELL_SIZE;
            canvas.height = rows * PIECE_CELL_SIZE;
            canvas.dataset.index = index;

            const pieceCtx = canvas.getContext('2d');
            drawPieceOnCanvas(pieceCtx, shape, piece.color, 0, 0, PIECE_CELL_SIZE);

            canvas.style.cursor = 'grab';
            canvas.addEventListener('mousedown', startDrag);
            canvas.addEventListener('touchstart', startDrag, { passive: false });

            slot.appendChild(canvas);
            pieceCanvases[index] = canvas;
        }
    });
}

function drawPieceOnCanvas(ctx, shape, colorKey, offsetX, offsetY, cellSize, isGhost = false) {
    shape.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            if (cell) {
                const x = offsetX + colIndex * cellSize;
                const y = offsetY + rowIndex * cellSize;

                if (isGhost) {
                    // Ghost piece - semi-transparent with border
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    roundRect(ctx, x + 2, y + 2, cellSize - 4, cellSize - 4, 4);
                    ctx.fill();
                    ctx.stroke();
                } else {
                    // Normal piece with gradient
                    const gradient = ctx.createLinearGradient(x, y, x + cellSize, y + cellSize);
                    gradient.addColorStop(0, COLORS[colorKey]);
                    gradient.addColorStop(1, shadeColor(COLORS[colorKey], -20));

                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    roundRect(ctx, x + 1, y + 1, cellSize - 2, cellSize - 2, 4);
                    ctx.fill();

                    // Add highlight
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                    ctx.beginPath();
                    roundRect(ctx, x + 3, y + 3, cellSize - 10, 4, 2);
                    ctx.fill();
                }
            }
        });
    });
}

function roundRect(ctx, x, y, width, height, radius) {
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function shadeColor(color, percent) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
}

function drawGrid() {
    // Clear canvas
    ctx.fillStyle = '#1e293b';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    // Draw grid cells
    for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
            const x = col * CELL_SIZE;
            const y = row * CELL_SIZE;

            if (grid[row][col]) {
                // Draw filled cell
                const colorKey = grid[row][col];
                const gradient = ctx.createLinearGradient(x, y, x + CELL_SIZE, y + CELL_SIZE);
                gradient.addColorStop(0, COLORS[colorKey]);
                gradient.addColorStop(1, shadeColor(COLORS[colorKey], -20));

                ctx.fillStyle = gradient;
                ctx.beginPath();
                roundRect(ctx, x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2, 6);
                ctx.fill();

                // Add highlight
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.beginPath();
                roundRect(ctx, x + 4, y + 4, CELL_SIZE - 12, 6, 3);
                ctx.fill();
            } else {
                // Draw empty cell with subtle border
                ctx.fillStyle = 'rgba(255, 255, 255, 0.02)';
                ctx.beginPath();
                roundRect(ctx, x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2, 6);
                ctx.fill();

                ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }

    // Draw ghost piece if dragging
    if (ghostPosition && draggedPiece) {
        const { row, col, valid } = ghostPosition;
        const ghostColor = valid ? 'rgba(0, 255, 100, 0.3)' : 'rgba(255, 50, 50, 0.3)';
        const ghostStroke = valid ? 'rgba(0, 255, 100, 0.6)' : 'rgba(255, 50, 50, 0.6)';

        draggedPiece.shape.forEach((shapeRow, r) => {
            shapeRow.forEach((cell, c) => {
                if (cell) {
                    const x = (col + c) * CELL_SIZE;
                    const y = (row + r) * CELL_SIZE;

                    // Check if this cell is within the grid
                    if (row + r >= 0 && row + r < GRID_SIZE && col + c >= 0 && col + c < GRID_SIZE) {
                        ctx.fillStyle = ghostColor;
                        ctx.strokeStyle = ghostStroke;
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        roundRect(ctx, x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4, 5);
                        ctx.fill();
                        ctx.stroke();
                    }
                }
            });
        });
    }
}

function setupEventListeners() {
    // Mouse events
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);

    // Touch events
    document.addEventListener('touchmove', drag, { passive: false });
    document.addEventListener('touchend', endDrag);

    // Restart button
    document.getElementById('restartBtn').addEventListener('click', restartGame);
}

function startDrag(e) {
    e.preventDefault();

    const canvas = e.target;
    draggedPieceIndex = parseInt(canvas.dataset.index);
    draggedPiece = currentPieces[draggedPieceIndex];

    if (!draggedPiece) return;

    const touch = e.touches ? e.touches[0] : e;
    const rect = canvas.getBoundingClientRect();

    // Calculate offset from where user clicked on the piece
    const offsetX = touch.clientX - rect.left;
    const offsetY = touch.clientY - rect.top;

    // Store this for proper snapping
    canvas.dataset.dragOffsetX = offsetX;
    canvas.dataset.dragOffsetY = offsetY;

    // Create dragging canvas
    const dragCanvas = document.createElement('canvas');
    dragCanvas.className = 'dragging-piece';
    dragCanvas.width = draggedPiece.shape[0].length * CELL_SIZE;
    dragCanvas.height = draggedPiece.shape.length * CELL_SIZE;

    const dragCtx = dragCanvas.getContext('2d');
    drawPieceOnCanvas(dragCtx, draggedPiece.shape, draggedPiece.color, 0, 0, CELL_SIZE);

    dragCanvas.style.left = (touch.clientX - dragCanvas.width / 2) + 'px';
    dragCanvas.style.top = (touch.clientY - dragCanvas.height / 2) + 'px';

    document.body.appendChild(dragCanvas);

    // Hide original piece
    canvas.style.opacity = '0.3';

    // Initial ghost calculation
    updateGhostPosition(touch.clientX, touch.clientY);
    drawGrid();
}

function drag(e) {
    if (!draggedPiece) return;

    e.preventDefault();

    const touch = e.touches ? e.touches[0] : e;
    const dragCanvas = document.querySelector('.dragging-piece');

    if (dragCanvas) {
        dragCanvas.style.left = (touch.clientX - dragCanvas.width / 2) + 'px';
        dragCanvas.style.top = (touch.clientY - dragCanvas.height / 2) + 'px';
    }

    // Update ghost position
    updateGhostPosition(touch.clientX, touch.clientY);
    drawGrid();
}

function updateGhostPosition(clientX, clientY) {
    if (!draggedPiece) {
        ghostPosition = null;
        return;
    }

    const gridRect = gameCanvas.getBoundingClientRect();

    // Calculate which grid cell the mouse is over
    const gridX = clientX - gridRect.left;
    const gridY = clientY - gridRect.top;

    // Calculate the center offset of the piece
    const pieceWidth = draggedPiece.shape[0].length * CELL_SIZE;
    const pieceHeight = draggedPiece.shape.length * CELL_SIZE;

    // Snap to nearest grid position (piece centered on cursor)
    const col = Math.round((gridX - pieceWidth / 2) / CELL_SIZE);
    const row = Math.round((gridY - pieceHeight / 2) / CELL_SIZE);

    // Check if this position is valid
    const valid = canPlacePiece(draggedPiece.shape, row, col);

    ghostPosition = { row, col, valid };
}

function endDrag(e) {
    if (!draggedPiece) return;

    const dragCanvas = document.querySelector('.dragging-piece');

    // Try to place piece at ghost position
    if (ghostPosition && ghostPosition.valid) {
        placePiece(draggedPiece.shape, draggedPiece.color, ghostPosition.row, ghostPosition.col);
        currentPieces[draggedPieceIndex] = null;

        // Check for lines to clear
        const linesCleared = checkAndClearLines();

        // Update streak: increment if lines were cleared, reset otherwise
        if (linesCleared > 0) {
            streakCount++;
        } else {
            streakCount = 0;
        }

        // Check if all pieces used
        if (currentPieces.every(p => p === null)) {
            generateNewPieces();
        } else {
            renderPieces();
        }

        // Check for game over
        checkGameOver();
    }

    // Remove dragging canvas
    if (dragCanvas) {
        dragCanvas.remove();
    }

    // Reset piece opacity
    if (pieceCanvases[draggedPieceIndex]) {
        pieceCanvases[draggedPieceIndex].style.opacity = '1';
    }

    // Clear ghost and redraw
    ghostPosition = null;
    draggedPiece = null;
    draggedPieceIndex = -1;
    drawGrid();
}

function canPlacePiece(shape, startRow, startCol) {
    for (let r = 0; r < shape.length; r++) {
        for (let c = 0; c < shape[0].length; c++) {
            if (shape[r][c]) {
                const gridRow = startRow + r;
                const gridCol = startCol + c;

                // Check bounds
                if (gridRow < 0 || gridRow >= GRID_SIZE ||
                    gridCol < 0 || gridCol >= GRID_SIZE) {
                    return false;
                }

                // Check if cell is empty
                if (grid[gridRow][gridCol]) {
                    return false;
                }
            }
        }
    }
    return true;
}

function placePiece(shape, color, startRow, startCol) {
    for (let r = 0; r < shape.length; r++) {
        for (let c = 0; c < shape[0].length; c++) {
            if (shape[r][c]) {
                grid[startRow + r][startCol + c] = color;
            }
        }
    }

    drawGrid();
}

function checkAndClearLines() {
    const rowsToClear = [];
    const colsToClear = [];

    // Check rows
    for (let row = 0; row < GRID_SIZE; row++) {
        if (grid[row].every(cell => cell !== null)) {
            rowsToClear.push(row);
        }
    }

    // Check columns
    for (let col = 0; col < GRID_SIZE; col++) {
        let full = true;
        for (let row = 0; row < GRID_SIZE; row++) {
            if (!grid[row][col]) {
                full = false;
                break;
            }
        }
        if (full) {
            colsToClear.push(col);
        }
    }

    const totalLines = rowsToClear.length + colsToClear.length;

    if (totalLines > 0) {
        // Count total blocks cleared for scoring
        let blocksCleared = 0;

        // Count unique blocks in rows (accounting for overlap with columns)
        rowsToClear.forEach(row => {
            for (let col = 0; col < GRID_SIZE; col++) {
                if (grid[row][col]) {
                    blocksCleared++;
                }
            }
        });

        // Count additional blocks in columns that weren't in cleared rows
        colsToClear.forEach(col => {
            for (let row = 0; row < GRID_SIZE; row++) {
                if (grid[row][col] && !rowsToClear.includes(row)) {
                    blocksCleared++;
                }
            }
        });

        // Clear rows
        rowsToClear.forEach(row => {
            for (let col = 0; col < GRID_SIZE; col++) {
                grid[row][col] = null;
            }
        });

        // Clear columns
        colsToClear.forEach(col => {
            for (let row = 0; row < GRID_SIZE; row++) {
                grid[row][col] = null;
            }
        });

        // Calculate Block Blast score: 10 points per block + combo bonus
        const baseScore = blocksCleared * POINTS_PER_BLOCK;
        const comboBonus = COMBO_BONUS[Math.min(totalLines, 9)] || 100;
        const streakBonus = streakCount > 1 ? (streakCount - 1) * 5 : 0; // Small bonus for streaks

        const totalScore = baseScore + comboBonus + streakBonus;
        score += totalScore;

        // Show combo
        showCombo(totalLines, blocksCleared, comboBonus, streakCount);

        updateScore();
        drawGrid();

        return totalLines;
    }

    return 0;
}

function showCombo(lines, blocks, bonus, streak) {
    const comboDisplay = document.getElementById('comboDisplay');

    if (lines === 1 && streak <= 1) {
        return; // Don't show for single line without streak
    }

    let text = '';

    if (lines >= 2) {
        if (lines === 2) text += 'DOUBLE! ';
        else if (lines === 3) text += 'TRIPLE! ';
        else text += `${lines}x LINES! `;
    }

    if (streak > 1) {
        text += `STREAK x${streak} `;
    }

    text += `+${bonus}`;

    comboDisplay.textContent = text;
    comboDisplay.classList.add('show');

    setTimeout(() => {
        comboDisplay.classList.remove('show');
    }, 1200);
}

function updateScore() {
    document.getElementById('score').textContent = score;

    if (score > highScore) {
        highScore = score;
        localStorage.setItem('blockBlastHighScore', highScore);
        document.getElementById('highScore').textContent = highScore;
    }
}

function checkGameOver() {
    // Check if any remaining piece can be placed
    const availablePieces = currentPieces.filter(p => p !== null);

    if (availablePieces.length === 0) {
        return; // Will generate new pieces
    }

    let canPlaceAny = false;

    for (const piece of availablePieces) {
        for (let row = -2; row < GRID_SIZE + 2; row++) {
            for (let col = -2; col < GRID_SIZE + 2; col++) {
                if (canPlacePiece(piece.shape, row, col)) {
                    canPlaceAny = true;
                    break;
                }
            }
            if (canPlaceAny) break;
        }
        if (canPlaceAny) break;
    }

    if (!canPlaceAny) {
        showGameOver();
    }
}

function showGameOver() {
    document.getElementById('finalScore').textContent = score;
    document.getElementById('gameOverModal').classList.add('show');
}

function restartGame() {
    grid = Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(null));
    score = 0;
    streakCount = 0;

    document.getElementById('score').textContent = '0';
    document.getElementById('gameOverModal').classList.remove('show');

    generateNewPieces();
    drawGrid();
}

// Start game when page loads
window.addEventListener('load', init);
