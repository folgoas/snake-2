const GRID_SIZE = 20;
const GRID_COUNT = 40;
const WINDOW_SIZE = GRID_SIZE * GRID_COUNT;

const MOCKING_PHRASES = [
    "Tu appelles ça jouer ?",
    "Même mon grand-père fait mieux !",
    "T'as les doigts carrés ou quoi ?",
    "C'est tout ce que tu peux faire ?",
    "Retourne jouer à Pong...",
    "LOL, même pas niveau 1 !",
    "Un escargot irait plus vite !",
    "Tu devrais peut-être essayer Tetris...",
    "Pas terrible ton high score...",
    "Mon chat joue mieux que ça !",
    "C'était... intéressant ?",
    "Essaie avec les yeux ouverts !",
    "Faut appuyer sur les touches, tu sais ?",
    "On dirait un bug qui joue !",
    "404 : Talent non trouvé"
];

class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.canvas.width = WINDOW_SIZE;
        this.canvas.height = WINDOW_SIZE;
        this.ctx = this.canvas.getContext('2d');
        
        this.grid = new CyberpunkGrid(this.canvas);
        this.particles = new ParticleSystem();
        
        this.reset();
        this.setupEventListeners();
    }

    reset() {
        this.snake = [{x: GRID_COUNT/2, y: GRID_COUNT/2}];
        this.direction = {x: 1, y: 0};
        this.nextDirection = {x: 1, y: 0};
        this.food = this.spawnFood();
        this.score = 0;
        this.gameOver = false;
        document.getElementById('scoreValue').textContent = this.score;
        document.getElementById('gameOver').style.display = 'none';
        document.getElementById('mainMenu').style.display = 'none';
    }

    spawnFood() {
        let position;
        do {
            position = {
                x: Math.floor(Math.random() * GRID_COUNT),
                y: Math.floor(Math.random() * GRID_COUNT)
            };
        } while (this.snake.some(segment => segment.x === position.x && segment.y === position.y));
        return position;
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowUp':
                    if (this.direction.y === 0) this.nextDirection = {x: 0, y: -1};
                    break;
                case 'ArrowDown':
                    if (this.direction.y === 0) this.nextDirection = {x: 0, y: 1};
                    break;
                case 'ArrowLeft':
                    if (this.direction.x === 0) this.nextDirection = {x: -1, y: 0};
                    break;
                case 'ArrowRight':
                    if (this.direction.x === 0) this.nextDirection = {x: 1, y: 0};
                    break;
                case 'r':
                case 'R':
                    if (this.gameOver) this.reset();
                    break;
            }
        });
    }

    update() {
        if (this.gameOver) return;

        this.direction = this.nextDirection;
        this.grid.update();

        const head = {
            x: (this.snake[0].x + this.direction.x + GRID_COUNT) % GRID_COUNT,
            y: (this.snake[0].y + this.direction.y + GRID_COUNT) % GRID_COUNT
        };

        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver = true;
            document.getElementById('gameOver').style.display = 'block';
            document.getElementById('mockingText').textContent = MOCKING_PHRASES[Math.floor(Math.random() * MOCKING_PHRASES.length)];
            return;
        }

        this.snake.unshift(head);

        if (head.x === this.food.x && head.y === this.food.y) {
            this.score++;
            document.getElementById('scoreValue').textContent = this.score;
            this.food = this.spawnFood();
            this.particles.emit(head.x * GRID_SIZE + GRID_SIZE/2, head.y * GRID_SIZE + GRID_SIZE/2);
        } else {
            this.snake.pop();
        }

        this.particles.update();
    }

    draw() {
        // Fond
        this.ctx.fillStyle = '#190033';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Grille cyberpunk
        this.grid.draw();

        // Particules
        this.particles.draw(this.ctx);

        // Serpent
        this.snake.forEach((segment, i) => {
            const color = i === 0 ? '#ff1493' : '#00ffff';
            this.drawSegmentWithGlow(segment.x * GRID_SIZE, segment.y * GRID_SIZE, color);
        });

        // Nourriture avec effet de lueur
        this.drawSegmentWithGlow(this.food.x * GRID_SIZE, this.food.y * GRID_SIZE, '#39ff14');
    }

    drawSegmentWithGlow(x, y, color) {
        // Effet de lueur
        const gradient = this.ctx.createRadialGradient(
            x + GRID_SIZE/2, y + GRID_SIZE/2, 0,
            x + GRID_SIZE/2, y + GRID_SIZE/2, GRID_SIZE
        );
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, 'rgba(0,0,0,0)');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x - GRID_SIZE/2, y - GRID_SIZE/2, GRID_SIZE*2, GRID_SIZE*2);
        
        // Segment principal
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x+1, y+1, GRID_SIZE-2, GRID_SIZE-2);

        // Effet métallique
        this.ctx.fillStyle = 'rgba(255,255,255,0.4)';
        this.ctx.fillRect(x+1, y+1, GRID_SIZE-2, 2);
    }

    gameLoop() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}

function startGame(difficulty) {
    const game = new Game();
    const speeds = {
        'easy': 200,      // Plus lent
        'normal': 160,    // Plus lent
        'hard': 120       // Plus lent
    };
    
    // Mise à jour du serpent à vitesse réduite
    setInterval(() => game.update(), speeds[difficulty]);
    
    // Animation fluide à 60 FPS pour les effets visuels
    requestAnimationFrame(function animate() {
        game.draw();
        requestAnimationFrame(animate);
    });
}

// Afficher le menu principal au chargement
document.getElementById('mainMenu').style.display = 'block';
