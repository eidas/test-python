const gameBoard = document.getElementById('game-board');
const player = document.getElementById('player');
const scoreDisplay = document.getElementById('score');

let playerScore = 0;
let playerPosition = 275;
const playerSpeed = 10;
let bullets = [];
let invaderBullets = [];
let invaders = [];
const invaderRows = 4;
const invaderCols = 8;
let invaderDirection = 1;
const invaderSpeed = 5;
let invaderMoveInterval = 500; // ms
let lastInvaderMove = 0;
let gameOver = false;

// プレイヤーの移動と発射
document.addEventListener('keydown', (e) => {
    if (gameOver) return;
    if (e.key === 'ArrowLeft') {
        playerPosition -= playerSpeed;
        if (playerPosition < 0) playerPosition = 0;
    } else if (e.key === 'ArrowRight') {
        playerPosition += playerSpeed;
        if (playerPosition > 550) playerPosition = 550; // gameBoard.width - player.width
    }
    player.style.left = playerPosition + 'px';

    if (e.key === ' ' || e.key === 'Spacebar') { // スペースキーで発射
        createBullet();
    }
});

// プレイヤーの弾を作成
function createBullet() {
    const bullet = document.createElement('div');
    bullet.className = 'bullet';
    bullet.style.left = (playerPosition + 22.5) + 'px'; // プレイヤーの中央から
    bullet.style.bottom = '30px';
    gameBoard.appendChild(bullet);
    bullets.push({ element: bullet, x: playerPosition + 22.5, y: 30 });
}

// インベーダーの弾を作成
function createInvaderBullet(invader) {
    const bullet = document.createElement('div');
    bullet.className = 'bullet';
    bullet.style.backgroundColor = '#f00'; // 色を変える
    bullet.style.left = (invader.x + 12.5) + 'px';
    bullet.style.top = (invader.y + 20) + 'px';
    gameBoard.appendChild(bullet);
    invaderBullets.push({ element: bullet, x: invader.x + 12.5, y: invader.y + 20 });
}

// プレイヤーの弾の動きと当たり判定
function moveBullets() {
    bullets.forEach((bullet, bulletIndex) => {
        bullet.y += 5;
        if (bullet.y > 400) {
            bullet.element.remove();
            bullets.splice(bulletIndex, 1);
        } else {
            bullet.element.style.bottom = bullet.y + 'px';
            invaders.forEach((invader, invaderIndex) => {
                if (bullet.x > invader.x && bullet.x < invader.x + 30 && 400 - bullet.y < invader.y + 20 && 400 - bullet.y > invader.y) {
                    bullet.element.remove();
                    bullets.splice(bulletIndex, 1);
                    invader.element.remove();
                    invaders.splice(invaderIndex, 1);
                    playerScore += 10;
                    scoreDisplay.textContent = playerScore;
                }
            });
        }
    });
}

// インベーダーの弾の動きと当たり判定
function moveInvaderBullets() {
    invaderBullets.forEach((bullet, index) => {
        bullet.y += 3;
        if (bullet.y > 400) {
            bullet.element.remove();
            invaderBullets.splice(index, 1);
        } else {
            bullet.element.style.top = bullet.y + 'px';
            if (bullet.x > playerPosition && bullet.x < playerPosition + 50 && bullet.y > 370 && bullet.y < 390) {
                endGame(false);
            }
        }
    });
}

// インベーダーを作成
function createInvaders() {
    for (let row = 0; row < invaderRows; row++) {
        for (let col = 0; col < invaderCols; col++) {
            const invader = document.createElement('div');
            invader.className = 'invader';
            const x = col * 60 + 40;
            const y = row * 40 + 20;
            invader.style.left = x + 'px';
            invader.style.top = y + 'px';
            gameBoard.appendChild(invader);
            invaders.push({ element: invader, x: x, y: y, row: row, col: col });
        }
    }
}

// インベーダーの動きとゲームオーバー判定
function moveInvaders() {
    let edgeReached = false;
    invaders.forEach(invader => {
        invader.x += invaderSpeed * invaderDirection;
        if (invader.x < 0 || invader.x > 570) {
            edgeReached = true;
        }
        if (invader.y > 350) {
            endGame(false);
        }
    });

    if (edgeReached) {
        invaderDirection *= -1;
        invaders.forEach(invader => {
            invader.y += 20;
        });
    }

    invaders.forEach(invader => {
        invader.element.style.left = invader.x + 'px';
        invader.element.style.top = invader.y + 'px';
    });

    // ランダムなインベーダーが発射
    if (Math.random() < 0.02 && invaders.length > 0) {
        const shootingInvader = invaders[Math.floor(Math.random() * invaders.length)];
        createInvaderBullet(shootingInvader);
    }
}

// ゲーム終了処理
function endGame(isWin) {
    if (gameOver) return;
    gameOver = true;
    const message = isWin ? "勝利！" : "ゲームオーバー";
    alert(message + "\nスコア: " + playerScore);
}

// ゲームのメインループ
function gameLoop(timestamp) {
    if (gameOver) return;

    if (timestamp - lastInvaderMove > invaderMoveInterval) {
        moveInvaders();
        lastInvaderMove = timestamp;
    }
    moveBullets();
    moveInvaderBullets();

    if (invaders.length === 0 && !gameOver) {
        endGame(true);
    }

    requestAnimationFrame(gameLoop);
}

// ゲーム開始
createInvaders();
requestAnimationFrame(gameLoop);
