class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 1000;
        this.canvas.height = 700;
        
        // Game properties
        this.score = 0;
        this.highScore = 0;
        this.lives = 10;
        this.gameActive = true;
        this.bulletSpeed = 20;
        this.zombieSpeed = 2;
        this.planeSpeed = 20;

        this.initializeGame();
    }

    async initializeGame() {
        await this.loadHighScore();
        await this.loadAssets();

        // Start the game
        this.startGame();
    }

    async loadAssets() {
        await Promise.all([
            this.loadImages(),
            this.loadSounds()
        ]);
    }

    loadImages() {
        return new Promise((resolve) => {
            this.images = {
                plane: new Image(),
                simpleZombie: new Image(),
                hardZombie: new Image(),
                harderZombie: new Image()
            };
            
            let loadedImages = 0;
            const totalImages = Object.keys(this.images).length;
            
            const checkAllImagesLoaded = () => {
                loadedImages++;
                if (loadedImages === totalImages) {
                    resolve();
                }
            };
            
            this.images.plane.onload = checkAllImagesLoaded;
            this.images.simpleZombie.onload = checkAllImagesLoaded;
            this.images.hardZombie.onload = checkAllImagesLoaded;
            this.images.harderZombie.onload = checkAllImagesLoaded;
            
            this.images.plane.src = '../images/plane.png';
            this.images.simpleZombie.src = '../images/simple.png';
            this.images.hardZombie.src = '../images/hard.png';
            this.images.harderZombie.src = '../images/harder.png';
        });
    }

    loadSounds() {
        return new Promise((resolve) => {
            this.sounds = {
                shoot: new Audio('../sounds/mixkit-short-laser-gun-shot.wav'),
                hit: new Audio('../sounds/mixkit-hit.wav'),
                lifeLost: new Audio('../sounds/mixkit-negative-game-notification.wav'),
                gameOver: new Audio('../sounds/mixkit-arcade-retro-game-over.wav'),
                background: new Audio('../sounds/mixkit-background.mp3')
            };

            let loadedSounds = 0;
            const totalSounds = Object.keys(this.sounds).length;
            
            const checkAllSoundsLoaded = () => {
                loadedSounds++;
                if (loadedSounds === totalSounds) {
                    Object.values(this.sounds).forEach(sound => {
                        sound.volume = 0.3;
                    });
                    this.sounds.background.loop = true;
                    resolve();
                }
            };
            
            Object.values(this.sounds).forEach(sound => {
                sound.addEventListener('canplaythrough', checkAllSoundsLoaded, { once: true });
            });
        });
    }

    startGame() {
        // Game objectss
        this.plane = {
            x: this.canvas.width / 2,
            y: this.canvas.height - 50,
            width: 48,
            height: 48
        };
        this.bullets = [];
        this.zombies = [];
        
        this.setupControls();
        this.lastTime = 0;
        this.zombieSpawnTimer = 0;
        this.animate(0);

        // Start background musci
        const startAudio = () => {
            this.sounds.background.play().catch(e => console.log('Error playing background music:', e));
            document.removeEventListener('click', startAudio);
            document.removeEventListener('keydown', startAudio);
        };

        document.addEventListener('click', startAudio);
        document.addEventListener('keydown', startAudio);
    }

    async loadHighScore() {
        try {
            const savedScore = localStorage.getItem('zombieHighScore') || '0';
            this.highScore = parseInt(savedScore);
            document.getElementById('highScore').textContent = this.highScore;
        } catch (error) {
            console.error('Error loading high score:', error);
            this.highScore = 0;
            document.getElementById('highScore').textContent = '0';
        }
    }

    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (!this.gameActive) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.plane.x = Math.max(0, this.plane.x - this.planeSpeed);
                    break;
                case 'ArrowRight':
                    this.plane.x = Math.min(this.canvas.width - this.plane.width, this.plane.x + this.planeSpeed);
                    break;
                case 'ArrowUp':
                    this.plane.y = Math.max(0, this.plane.y - this.planeSpeed);
                    break;
                case 'ArrowDown':
                    this.plane.y = Math.min(this.canvas.height - this.plane.height, this.plane.y + this.planeSpeed);
                    break;
                case ' ':
                    this.shootBullet();
                    break;
            }
        });
    }

    shootBullet() {
        if (!this.gameActive) return;
        
        this.sounds.shoot.currentTime = 0;
        this.sounds.shoot.play();
        
        [-10, 0, 10].forEach(offset => {
            this.bullets.push({
                x: this.plane.x + this.plane.width/2 + offset,
                y: this.plane.y - 10,
                width: 4,
                height: 10
            });
        });
    }

    spawnZombie() {
        const zombieTypes = [
            { img: this.images.harderZombie, difficulty: 0.2, hitPoints: 5 },
            { img: this.images.hardZombie, difficulty: 0.3, hitPoints: 3 },
            { img: this.images.simpleZombie, difficulty: 0.4, hitPoints: 1 }
        ];
        
        const zombie = zombieTypes[Math.floor(Math.random() * zombieTypes.length)];
        this.zombies.push({
            x: Math.random() * (this.canvas.width - 48),
            y: 0,
            width: 48,
            height: 48,
            difficulty: zombie.difficulty,
            hitPoints: zombie.hitPoints,
            img: zombie.img
        });
    }

    resetPlanePosition() {
        this.plane.x = this.canvas.width / 2;
        this.plane.y = this.canvas.height - 50;
    }

    updateBullets() {
        this.bullets = this.bullets.filter(bullet => {
            bullet.y -= this.bulletSpeed;
            return bullet.y > 0;
        });
    }

    updateZombies() {
        this.zombies = this.zombies.filter(zombie => {
            zombie.y += zombie.difficulty;
            
            // Check if bullets hit zombie
            for (let i = this.bullets.length - 1; i >= 0; i--) {
                const bullet = this.bullets[i];
                if (this.checkCollision(bullet, zombie)) {
                    this.sounds.hit.currentTime = 0;
                    this.sounds.hit.play();
                    zombie.hitPoints--;
                    this.bullets.splice(i, 1);
                    
                    if (zombie.hitPoints <= 0) {
                        this.score += 2;
                        this.updateScore();
                        return false;
                    }
                }
            }
            
            // Check plane hit with zombie
            if (this.checkCollision(this.plane, zombie)) {
                this.loseLife();
                this.resetPlanePosition();
                return false;
            }
            
            // Check if zombie pass bottom canvas
            if (zombie.y > this.canvas.height) {
                this.loseLife();
                return false;
            }
            
            return true;
        });
    }

    checkCollision(obj1, obj2) {
        return obj1.x < obj2.x + obj2.width &&
               obj1.x + obj1.width > obj2.x &&
               obj1.y < obj2.y + obj2.height &&
               obj1.y + obj1.height > obj2.y;
    }

    loseLife() {
        this.sounds.lifeLost.currentTime = 0;
        this.sounds.lifeLost.play();
        this.lives--;
        document.getElementById('lives').textContent = this.lives;
        
        if (this.lives <= 0) {
            this.gameOver();
        }
    }

    async gameOver() {
        this.gameActive = false;
        
        // Play game over sound
        await new Promise(resolve => {
            this.sounds.gameOver.play();
            this.sounds.gameOver.onended = resolve;
        });

        if (this.score > this.highScore) {
            this.highScore = this.score;
            try {
                localStorage.setItem('zombieHighScore', this.highScore.toString());
                document.getElementById('highScore').textContent = this.highScore;
            } catch (error) {
                console.error('Error saving high score:', error);
            }
        }

        // Ask to play again
        if (confirm(`Game Over! Final Score: ${this.score}\nPlay again?`)) {
            this.restartGame();
        }
    }

    restartGame() {
        this.score = 0;
        document.getElementById('score').textContent = '0';
        this.lives = 10;
        document.getElementById('lives').textContent = '10';
        this.gameActive = true;
        this.bullets = [];
        this.zombies = [];
        this.resetPlanePosition();
        
        // play background music
        if (this.sounds.background.paused) {
            this.sounds.background.currentTime = 0;
            this.sounds.background.play().catch(e => console.log('Error playing background music:', e));
        }
  
        this.lastTime = 0;
        requestAnimationFrame((time) => this.animate(time));
    }

    updateScore() {
        document.getElementById('score').textContent = this.score;
        if (this.score > this.highScore) {
            this.highScore = this.score;
            document.getElementById('highScore').textContent = this.highScore;
        }
    }

    draw() {
        this.ctx.fillStyle = 'black';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // draw plane
        this.ctx.drawImage(this.images.plane, this.plane.x, this.plane.y, this.plane.width, this.plane.height);
        
        // Draw bullets
        this.ctx.fillStyle = 'gold';
        this.bullets.forEach(bullet => {
            this.ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
        });
        
        // Draw zombies
        this.zombies.forEach(zombie => {
            this.ctx.drawImage(zombie.img, zombie.x, zombie.y, zombie.width, zombie.height);
        });
    }

    animate(currentTime) {
        const deltaTime = currentTime - this.lastTime;
        
        if (deltaTime >= 1000) {
            this.spawnZombie();
            this.lastTime = currentTime;
        }
        
        if (this.gameActive) {
            this.updateBullets();
            this.updateZombies();
            this.draw();
            requestAnimationFrame((time) => this.animate(time));
        }
    }
}

// Start the game after assetts are loaded
window.addEventListener('load', () => {
    new Game();
});