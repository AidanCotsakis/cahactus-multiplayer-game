# Multiplayer Cacti Game (Unfinished)

A real-time multiplayer game where players control cacti characters that can move and shoot projectiles. Built with Python and Pygame, this game uses a client-server model to handle multiple players in a shared environment.

## **Features**

- **Multiplayer Real-time Gameplay**  
  Supports multiple players interacting in a single shared world, managed by a central server.

- **Dynamic Player Movement**  
  Players can navigate using arrow keys, with velocity limits and boundary enforcement.

- **Projectile Shooting Mechanic**  
  Each player can launch projectiles, tracked for movement and collision across the game world.

- **Custom Sprites and Backgrounds**  
  Includes tailored sprites for characters, shadows, and backgrounds to enhance the gameplay experience.

## **Installation**

1. **Clone the repository**.
2. **Ensure Python (3.x recommended) is installed**.
3. **Install required libraries**:
    ```bash
    pip install pygame
    ```
4. **Set Server IP**

    In `client.py`, configure the host variable in the Network class to point to the server IP address:
    ```python
    self.host = "your_server_ip"
    ```

## **Usage**
1. **Run the Server**

    Start the server by running `server.py`:

    ```bash
    python server.py
    ```

2. **Run the Client**

    Each player runs a client by launching `game.py`:

    ```bash
    python game.py
    ```
3. **Game Controls**
    - **Movement**: `Arrow keys` or `W`, `A`, `S`, `D`
    - **Shoot Projectile**: `Left mouse button`

## **Game Mechanics**
- **Player Movement**: Movement speeds vary based on key combinations, with enforced boundary checks.
- **Shooting Projectiles**: Each player can launch up to two projectiles, controlled by mouse clicks.
- **Particle Effects**: Adds dynamic particle effects to enhance visual impact around player movements.
- **Server-Client Data Sync**: Server regularly updates client positions, maintaining a consistent game state across all connections.