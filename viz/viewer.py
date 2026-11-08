"""
Pygame viewer for the Desert Rescue Drone. PROVIDED - you do not need to edit it.

    python main.py --id YOUR_ID --phase mission --gui            watch the mission live
    python main.py --id YOUR_ID --phase mission --save map.png   save the final picture

Legend
    sand / rocks / dunes / mountain   background colours
    red shading                       belief that the hiker is there (darker = more likely)
    green dot                         cell proved SAFE by your KB
    purple X                          cell proved to be a SANDSTORM by your KB
    blue line                         the drone's trail
    B base   O oasis   L last phone signal   H hiker (shown when found or at the end)
"""

from __future__ import annotations

import os
from typing import Optional

from world.desert_map import DUNE, MOUNTAIN, ROCK, SAND

CELL = 34
PANEL = 250
COLORS = {
    SAND: (238, 217, 164),
    ROCK: (168, 159, 145),
    DUNE: (217, 168, 91),
    MOUNTAIN: (91, 70, 54),
}


class Viewer:
    def __init__(self, world, headless: bool = False, title: str = "Desert Rescue Drone"):
        if headless:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
        self.pg = pygame
        pygame.init()
        self.world = world
        size = (world.cols * CELL + PANEL, world.rows * CELL)
        self.screen = pygame.display.set_mode(size) if not headless else pygame.Surface(size)
        if not headless:
            pygame.display.set_caption(title)
        self.font = pygame.font.SysFont("arial", 15)
        self.big = pygame.font.SysFont("arial", 18, bold=True)
        self.clock = pygame.time.Clock()
        self.headless = headless

    def _center(self, cell):
        r, c = cell
        return c * CELL + CELL // 2, r * CELL + CELL // 2

    def _label(self, cell, text, color=(20, 20, 20)):
        img = self.big.render(text, True, color)
        x, y = self._center(cell)
        self.screen.blit(img, img.get_rect(center=(x, y)))

    def draw(self, drone=None, reveal: bool = False, status: str = "") -> None:
        pg, w, scr = self.pg, self.world, self.screen
        scr.fill((250, 248, 242))
        top = max(drone.belief.values()) if drone else 1.0
        for r in range(w.rows):
            for c in range(w.cols):
                cell = (r, c)
                rect = pg.Rect(c * CELL, r * CELL, CELL, CELL)
                pg.draw.rect(scr, COLORS[w.grid[r][c]], rect)
                if drone and w.grid[r][c] != MOUNTAIN:
                    p = drone.belief.get(cell, 0.0) / top if top > 0 else 0
                    if p > 0.02:
                        shade = pg.Surface((CELL, CELL), pg.SRCALPHA)
                        shade.fill((200, 30, 30, int(170 * p)))
                        scr.blit(shade, rect)
                pg.draw.rect(scr, (200, 190, 170), rect, 1)
        if drone:
            for cell in drone.safety.safe_cells():
                pg.draw.circle(scr, (30, 150, 60), self._center(cell), 4)
            for cell in drone.safety.storm_cells():
                x, y = self._center(cell)
                pg.draw.line(scr, (120, 40, 160), (x - 10, y - 10), (x + 10, y + 10), 4)
                pg.draw.line(scr, (120, 40, 160), (x - 10, y + 10), (x + 10, y - 10), 4)
            if len(drone.trail) > 1:
                pg.draw.lines(scr, (30, 80, 200), False, [self._center(c) for c in drone.trail], 3)
        if reveal:
            for cell in w.storms:
                pg.draw.circle(scr, (90, 60, 120), self._center(cell), CELL // 2 - 3, 3)
        self._label(w.last_signal, "L", (150, 0, 0))
        self._label(w.oasis, "O", (0, 70, 170))
        self._label(w.base, "B")
        if w.hiker and (reveal or (drone and drone.found)):
            self._label(w.hiker, "H", (200, 0, 0))
        if drone:
            pg.draw.circle(scr, (255, 255, 255), self._center(drone.pos), 10)
            pg.draw.circle(scr, (30, 80, 200), self._center(drone.pos), 10, 3)
        self._panel(drone, status)
        if not self.headless:
            pg.display.flip()

    def _panel(self, drone, status: str) -> None:
        x0 = self.world.cols * CELL + 12
        lines = [f"Map seed: {self.world.seed}"]
        if drone:
            lines += [f"Battery: {drone.battery:.0f}", f"Cells flown: {drone.cells_flown}",
                      f"Scans: {drone.scans}", f"Proved safe: {len(drone.safety.safe_cells())}",
                      f"Proved storms: {len(drone.safety.storm_cells())}"]
            if drone.frames:
                lines += ["", "Last event:"] + _wrap(drone.frames[-1].event, 28)
        if status:
            lines += ["", "Status:"] + _wrap(status, 28)
        lines += ["", "Legend:", "red = belief", "green dot = safe", "purple X = storm",
                  "B base  O oasis", "L last signal  H hiker"]
        y = 12
        for line in lines:
            self.screen.blit(self.font.render(line, True, (30, 30, 30)), (x0, y))
            y += 20

    def tick(self, fps: int = 12) -> bool:
        """Show the frame; return False if the window was closed."""
        if self.headless:
            return True
        for event in self.pg.event.get():
            if event.type == self.pg.QUIT:
                return False
        self.clock.tick(fps)
        return True

    def wait_for_close(self) -> None:
        if self.headless:
            return
        while self.tick(30):
            pass

    def save(self, path: str) -> None:
        self.pg.image.save(self.screen, path)


def _wrap(text: str, width: int):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > width:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        lines.append(cur)
    return lines
