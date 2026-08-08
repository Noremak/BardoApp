"""
.31 ver
"""

import sys
import pygame
import math
import random
import array
import colorsys

def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(64)

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("Bardo")
    clock = pygame.time.Clock()

    # import pygame
import math
import random
import array
import colorsys

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(64)

# Android compatibility: Fullscreen and auto-scaling to device resolution
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Bardo: Indra's Net")
clock = pygame.time.Clock()

POINTS_PER_TIER = 600.0
MAX_CONSCIOUSNESS = 3000.0 

# --- Hyper-Acoustic Matrix ---
tone_bank = {}
chime_bank = {}
drone_bank = {}

for i in range(10, 51):
    hz = i * 10 
    sample_rate = 44100
    
    buf_tone = array.array('h')
    for s in range(sample_rate):
        t = float(s) / sample_rate
        left = int(0.06 * 32767.0 * math.sin(2.0 * math.pi * (hz - 0.5) * t))
        right = int(0.06 * 32767.0 * math.sin(2.0 * math.pi * (hz + 0.5) * t))
        buf_tone.append(left)
        buf_tone.append(right)
    tone_bank[i] = pygame.mixer.Sound(buffer=buf_tone.tobytes())
    
    buf_drone = array.array('h')
    for s in range(sample_rate):
        t = float(s) / sample_rate
        wave = (
            0.6 * math.sin(2.0 * math.pi * hz * t) +
            0.3 * math.sin(2.0 * math.pi * hz * 1.5 * t) + 
            0.2 * math.sin(2.0 * math.pi * hz * 1.25 * t) +
            0.1 * math.sin(2.0 * math.pi * hz * 2.0 * t)   
        )
        sample = int(0.025 * 32767.0 * wave) 
        buf_drone.append(sample)
        buf_drone.append(sample)
    drone_bank[i] = pygame.mixer.Sound(buffer=buf_drone.tobytes())

    duration = 6.0
    total_samples = int(sample_rate * duration)
    buf_chime = array.array('h')
    for s in range(total_samples):
        t = s / sample_rate
        env = (1.0 - math.exp(-50.0 * t)) * math.exp(-0.6 * t)
        wave = (
            1.00 * math.sin(2.0 * math.pi * hz * 1.00 * t) +
            0.60 * math.sin(2.0 * math.pi * hz * 1.50 * t) +
            0.30 * math.sin(2.0 * math.pi * hz * 1.666 * t) +
            0.15 * math.sin(2.0 * math.pi * hz * 2.00 * t)
        ) * env
        sample = int(0.12 * 32767.0 * max(-1.0, min(1.0, wave)))
        buf_chime.append(sample)
        buf_chime.append(sample)
    chime_bank[i] = pygame.mixer.Sound(buffer=buf_chime.tobytes())

def get_harmonic_ratio(index):
    ratios = [1.0, 1.25, 1.333, 1.5, 1.666, 1.875, 2.0, 2.5]
    return ratios[index % len(ratios)]

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))

def freq_to_color(freq, tier, progress):
    norm = (freq - 1.0) / 4.0
    hue = norm * 0.85 
    
    if tier == 0:
        sat = max(0.2, 0.9 - (progress * 0.7))
        val = 0.9
    elif tier == 1:
        hue = 0.55 + (norm * 0.1) 
        sat = max(0.1, 0.8 - progress)
        val = 0.95
    elif tier == 2:
        hue = 0.1 
        sat = 0.0
        val = 1.0
    else:
        hue = (norm + progress * 2.0) % 1.0
        sat = min(1.0, (tier - 2) * 0.5)
        val = 1.0
        
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return (int(r*255), int(g*255), int(b*255))

class BardoField:
    def __init__(self):
        self.nodes = []
        for _ in range(150):
            self.nodes.append({
                'x': random.uniform(-2000, 3000),
                'y': random.uniform(-2000, 3000),
                'z': random.uniform(0.1, 1.0),
                'phase': random.uniform(0, math.pi * 2)
            })

    def draw(self, surface, cam_x, cam_y, tier, tier_progress, total_progress, space_rotation):
        if tier >= 4:
            pulse = (math.sin(pygame.time.get_ticks() * 0.001) + 1.0) * 0.5
            bg_v = int(lerp(20, 255, tier_progress * pulse))
            surface.fill((bg_v, bg_v, bg_v))
        else:
            void_depth = total_progress * 1.5
            bg_r = int(25 * (1.0 - min(1.0, void_depth)))
            bg_g = int(35 * (1.0 - min(1.0, void_depth)))
            bg_b = int(45 * (1.0 - min(1.0, void_depth)))
            surface.fill((bg_r, bg_g, bg_b))

        time_val = pygame.time.get_ticks() * 0.0003 
        
        projected = []
        cx_s, cy_s = WIDTH / 2, HEIGHT / 2

        for n in self.nodes:
            nx = n['x'] - cam_x * n['z']
            ny = n['y'] - cam_y * n['z']
            
            if space_rotation != 0:
                rx = (nx - cx_s) * math.cos(space_rotation) - (ny - cy_s) * math.sin(space_rotation) + cx_s
                ry = (nx - cx_s) * math.sin(space_rotation) + (ny - cy_s) * math.cos(space_rotation) + cy_s
                nx, ny = rx, ry

            px = nx % WIDTH
            py = ny % HEIGHT
            pulse = (math.sin(time_val + n['phase']) + 1) * 0.5
            projected.append((px, py, n['z'], pulse))
            
            radius = int(2 * n['z'] + pulse * 2)
            
            if tier >= 4:
                alpha = int(255 * (1.0 - pulse))
                color = (0, 0, 0, alpha)
            else:
                alpha = int(255 * (1.0 - min(1.0, total_progress * 1.2)))
                color = (int(40 + pulse*20), int(60 + pulse*30), int(100 + pulse*50), alpha)
            
            if alpha > 10:
                surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (radius, radius), radius)
                surface.blit(surf, (px - radius, py - radius))

        if tier == 1 or tier == 2:
            connect_alpha = int(80 * math.sin(tier_progress * math.pi))
            if connect_alpha > 0:
                for i in range(len(projected)):
                    for j in range(i + 1, len(projected)):
                        p1, p2 = projected[i], projected[j]
                        dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                        if dist < 180:
                            pygame.draw.line(surface, (100, 150, 255, connect_alpha), (p1[0], p1[1]), (p2[0], p2[1]), 1)

class Satellite:
    def __init__(self, angle_offset, harmonic_index, channel_id, root_freq):
        self.angle_offset = angle_offset
        self.harmonic_index = harmonic_index
        self.channel = pygame.mixer.Channel(channel_id)
        self.current_freq_key = -1
        self.dist = random.uniform(80, 150)
        self.orbit_speed = random.uniform(0.3, 1.2)
        self.update_audio(root_freq)
        
    def update_audio(self, root_freq):
        ratio = get_harmonic_ratio(self.harmonic_index)
        target_freq = root_freq * ratio
        while target_freq > 5.0: target_freq *= 0.5 
        
        new_key = int(round(target_freq * 10))
        if new_key != self.current_freq_key and new_key in drone_bank:
            self.current_freq_key = new_key
            self.channel.play(drone_bank[new_key], loops=-1)

    def draw(self, surface, cx, cy, time_val, tier, tier_prog, scale=1.0):
        angle = time_val * self.orbit_speed + self.angle_offset
        breathe = math.sin(time_val * 1.5 + self.angle_offset) * 15 * scale
        px = cx + math.cos(angle) * (self.dist * scale + breathe)
        py = cy + math.sin(angle) * (self.dist * scale + breathe)
        
        color = freq_to_color(max(10, self.current_freq_key) / 10.0, tier, tier_prog)
        if tier >= 4:
            pygame.draw.circle(surface, (0, 0, 0), (int(px), int(py)), int(8 * scale))
            pygame.draw.line(surface, (0, 0, 0, 150), (cx, cy), (px, py), 2)
        else:
            pygame.draw.circle(surface, color, (int(px), int(py)), int(5 * scale))
            pygame.draw.line(surface, (*color, 120), (cx, cy), (px, py), 1)

class Shadow:
    def __init__(self, x, y, channel_id, forced_freq=None):
        self.x, self.y = x, y
        self.freq = forced_freq if forced_freq else round(random.uniform(1.0, 5.0), 1)
        self.amp = round(random.uniform(15.0, 30.0), 1)
        self.integrated = False
        
        self.channel_id = channel_id
        self.channel = pygame.mixer.Channel(channel_id)
        
        self.freq_key = int(round(self.freq * 10))
        if self.freq_key in tone_bank:
            self.channel.play(tone_bank[self.freq_key], loops=-1)
        
        angle = random.uniform(0, math.pi * 2)
        self.vx = math.cos(angle) * 0.03 
        self.vy = math.sin(angle) * 0.03

    def update(self, is_mirror=False, target_vx=0, target_vy=0):
        if is_mirror:
            self.vx = lerp(self.vx, target_vx * 0.8, 0.05)
            self.vy = lerp(self.vy, target_vy * 0.8, 0.05)
        else:
            self.vx += random.uniform(-0.0015, 0.0015)
            self.vy += random.uniform(-0.0015, 0.0015)
            
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.99
        self.vy *= 0.99

    def destroy(self):
        if self.channel.get_busy():
            self.channel.stop()

class Observer:
    def __init__(self):
        self.x, self.y = 0.0, 0.0
        self.vx, self.vy = 0.0, 0.0
        self.phase_freq = 1.0
        self.phase_amp = 10.0
        
        self.channel = pygame.mixer.Channel(0)
        self.channel.play(tone_bank[10], loops=-1)
        
        self.total_consciousness = 0.0
        self.satellites = []
        self.sat_channel_start = 30
        self.space_rotation = 0.0
        
        # Joystick UI parameters
        self.joy_center = (WIDTH - 150, HEIGHT - 150)
        self.joy_radius = 100
        self.knob_pos = self.joy_center

    def get_tier_state(self):
        tier = int(self.total_consciousness // POINTS_PER_TIER)
        progress = (self.total_consciousness % POINTS_PER_TIER) / POINTS_PER_TIER
        total = min(1.0, self.total_consciousness / MAX_CONSCIOUSNESS)
        return min(4, tier), progress if tier < 4 else 1.0, total

    def add_satellite(self):
        idx = len(self.satellites)
        ch = self.sat_channel_start + idx
        if ch < 64:
            sat = Satellite(random.uniform(0, math.pi*2), idx, ch, self.phase_freq)
            self.satellites.append(sat)

    def update_touch(self, active_touches):
        tier, tier_prog, total_prog = self.get_tier_state()
        glide_factor = 0.996 + (total_prog * 0.0035) 
        
        joystick_active = False
        
        for touch_id, (tx, ty) in active_touches.items():
            dist_to_joy = math.hypot(tx - self.joy_center[0], ty - self.joy_center[1])
            
            # Check if touch is engaging the joystick
            if dist_to_joy <= self.joy_radius * 1.5:
                joystick_active = True
                
                # Clamp knob to joystick radius
                angle = math.atan2(ty - self.joy_center[1], tx - self.joy_center[0])
                dist = min(dist_to_joy, self.joy_radius)
                self.knob_pos = (self.joy_center[0] + math.cos(angle) * dist, 
                                 self.joy_center[1] + math.sin(angle) * dist)
                
                # Map Cartesian coordinates to Amp and Freq
                norm_x = (self.knob_pos[0] - self.joy_center[0]) / self.joy_radius
                norm_y = (self.knob_pos[1] - self.joy_center[1]) / self.joy_radius
                
                # Left/Right -> Amplitude (10 to 40)
                self.phase_amp = max(10.0, min(40.0, 25.0 + (norm_x * 15.0)))
                # Up/Down -> Frequency (1 to 5). Negative Y is Up in screen coords.
                self.phase_freq = max(1.0, min(5.0, 3.0 + (-norm_y * 2.0)))
                
            else:
                # Touch outside joystick acts as gravitational movement pull
                if tier >= 4:
                    self.space_rotation += (tx - WIDTH/2) * 0.00005
                    if random.random() < 0.05:
                        chime_ch = pygame.mixer.find_channel(True)
                        if chime_ch:
                            rand_f = random.choice([self.phase_freq, self.phase_freq*1.5, self.phase_freq*2.0])
                            while rand_f > 5.0: rand_f *= 0.5
                            k = int(round(rand_f * 10))
                            if k in chime_bank: chime_ch.play(chime_bank[k])
                        bursts.append(Burst(WIDTH/2 + random.uniform(-200, 200), HEIGHT/2 + random.uniform(-200, 200), (0,0,0)))
                else:
                    accel = 0.014 - (total_prog * 0.008)
                    angle = math.atan2(ty - HEIGHT/2, tx - WIDTH/2)
                    self.vx += math.cos(angle) * accel
                    self.vy += math.sin(angle) * accel

        if not joystick_active:
            # Gradually snap joystick back to center if released
            self.knob_pos = (
                lerp(self.knob_pos[0], self.joy_center[0], 0.1),
                lerp(self.knob_pos[1], self.joy_center[1], 0.1)
            )

        self.vx *= glide_factor
        self.vy *= glide_factor
        self.x += self.vx
        self.y += self.vy

        old_freq_key = int(round(self.phase_freq * 10))
        self.phase_freq = round(self.phase_freq, 2)
        new_freq_key = int(round(self.phase_freq * 10))
        
        if new_freq_key != old_freq_key and new_freq_key in tone_bank:
            self.channel.play(tone_bank[new_freq_key], loops=-1)
            
        for sat in self.satellites:
            sat.update_audio(self.phase_freq)

    def draw_joystick(self, surface, tier, tier_prog):
        if tier >= 4: return # Joystick vanishes in the void
        
        joy_surf = pygame.Surface((self.joy_radius * 2.5, self.joy_radius * 2.5), pygame.SRCALPHA)
        center = self.joy_radius * 1.25
        
        color = freq_to_color(self.phase_freq, tier, tier_prog)
        
        # Base Ring
        pygame.draw.circle(joy_surf, (*color[:3], 40), (int(center), int(center)), self.joy_radius, 2)
        
        # Dynamic Aura based on amplitude
        aura_rad = int(self.joy_radius * (self.phase_amp / 40.0))
        pygame.draw.circle(joy_surf, (*color[:3], 20), (int(center), int(center)), aura_rad)
        
        # The Knob
        kx = center + (self.knob_pos[0] - self.joy_center[0])
        ky = center + (self.knob_pos[1] - self.joy_center[1])
        pygame.draw.circle(joy_surf, (*color[:3], 150), (int(kx), int(ky)), 20)
        pygame.draw.circle(joy_surf, (255, 255, 255, 200), (int(kx), int(ky)), 20, 2)
        
        surface.blit(joy_surf, (self.joy_center[0] - center, self.joy_center[1] - center))

class Burst:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.radius = 10
        self.life = 255

    def update(self):
        self.radius += 5.0
        self.life -= 3.0

    def draw(self, surface, cx, cy):
        if self.life > 0:
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], int(self.life)), (int(self.radius), int(self.radius)), int(self.radius), 4)
            surface.blit(s, (int(self.x - cx - self.radius), int(self.y - cy - self.radius)))

def draw_chladni_entity(surface, cx, cy, freq, amp, time_val, tier, tier_prog, is_player=False):
    color = freq_to_color(freq, tier, tier_prog)
    base_radius = 20 + amp
    
    entity_surf = pygame.Surface((int(base_radius * 5), int(base_radius * 5)), pygame.SRCALPHA)
    center = base_radius * 2.5
    
    line_w = 3 if is_player else 2

    if tier < 2:
        n = max(2, int(freq * 1.5))
        m = max(2, int(freq * 2.0))
        pts = []
        res = 120
        for i in range(res):
            angle = (i / res) * math.pi * 2
            r_node = base_radius * (0.5 + 0.5 * abs(math.sin(n * angle + time_val) * math.cos(m * angle - time_val)))
            pts.append((center + math.cos(angle) * r_node, center + math.sin(angle) * r_node))
        if len(pts) > 2:
            pygame.draw.lines(entity_surf, color, True, pts, line_w)
    elif tier == 2:
        sides = max(3, int(freq * 1.5))
        pts = []
        for i in range(sides):
            angle = (i / sides) * math.pi * 2 + time_val
            pts.append((center + math.cos(angle) * base_radius, center + math.sin(angle) * base_radius))
        pygame.draw.polygon(entity_surf, color, pts, line_w)
        pygame.draw.circle(entity_surf, color, (int(center), int(center)), int(base_radius * 0.5), 1)
    else:
        cube_size = base_radius * 0.8
        offset = cube_size * 0.5 * math.sin(time_val * 2.0)
        
        for i in range(2):
            s_size = cube_size if i == 0 else cube_size * 0.5
            cx_sq = center + (offset if i == 1 else 0)
            cy_sq = center + (offset if i == 1 else 0)
            
            pts = []
            for j in range(4):
                ang = (j * math.pi / 2) + time_val * (1.0 if i==0 else -1.0)
                pts.append((cx_sq + math.cos(ang)*s_size, cy_sq + math.sin(ang)*s_size))
            pygame.draw.polygon(entity_surf, color, pts, line_w)
            
            if i == 1:
                outer_pts = []
                for j in range(4):
                    ang = (j * math.pi / 2) + time_val
                    outer_pts.append((center + math.cos(ang)*cube_size, center + math.sin(ang)*cube_size))
                for k in range(4):
                    pygame.draw.line(entity_surf, color, pts[k], outer_pts[k], 1)

    if tier == 3:
        glitch_x = (math.sin(time_val * 20.0) * 10.0) * tier_prog
        surface.blit(entity_surf, (int(cx - center + glitch_x), int(cy - center)), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(entity_surf, (int(cx - center - glitch_x), int(cy - center)), special_flags=pygame.BLEND_RGBA_ADD)
    else:
        surface.blit(entity_surf, (int(cx - center), int(cy - center)))


def draw_central_mandala(surface, x, y, progress, satellites, time_val, tier):
    if progress < 0.01: return
    
    is_transcendent = tier >= 4
    mig_t = max(0.0, min(1.0, (progress - 0.5) * 2.0)) 
    
    target_x = lerp(WIDTH - 180, WIDTH / 2, mig_t)
    target_y = lerp(180, HEIGHT / 2, mig_t)
    
    if is_transcendent:
        radius = lerp(120, 800, progress)
    else:
        radius = 40 + (mig_t * 180)
        
    mandala_surf = pygame.Surface((int(radius*8), int(radius*8)), pygame.SRCALPHA)
    cx, cy = radius * 4, radius * 4
    
    if is_transcendent:
        color = (0, 0, 0, 180) 
    else:
        alpha = int(255 * min(1.0, progress * 2.0))
        color = (240, 245, 255, alpha)
    
    pygame.draw.circle(mandala_surf, color, (int(cx), int(cy)), int(radius), 2 if is_transcendent else 1)
    
    layers = int(progress * 15)
    for l in range(layers):
        r_layer = radius * (1.0 + (l * 0.2)) + (math.sin(time_val + l) * 10 * mig_t)
        nodes = 6 + (l * 6)
        for n in range(nodes):
            angle = (n / nodes) * math.pi * 2 + (time_val * 0.2 * (-1 if l%2==0 else 1))
            px = cx + math.cos(angle) * r_layer
            py = cy + math.sin(angle) * r_layer
            
            node_color = (*color[:3], int(color[3] * 0.4))
            pygame.draw.circle(mandala_surf, node_color, (int(px), int(py)), int(radius * 0.3), 1)
            
            if n < len(satellites) * 3:
                pygame.draw.line(mandala_surf, (*color[:3], int(color[3] * 0.2)), (cx, cy), (px, py), 1)

    surface.blit(mandala_surf, (int(target_x - cx), int(target_y - cy)))


bardo = BardoField()
observer = Observer()
shadows = []
bursts = []
active_touches = {}

running = True
while running:
    time_val = pygame.time.get_ticks() * 0.001 
    
    # Touch Event Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
            # Finger positions are normalized 0.0 to 1.0, convert to screen pixels
            active_touches[event.finger_id] = (event.x * WIDTH, event.y * HEIGHT)
        elif event.type == pygame.FINGERUP:
            if event.finger_id in active_touches:
                del active_touches[event.finger_id]

    observer.update_touch(active_touches)
    
    tier, tier_prog, total_prog = observer.get_tier_state()

    if tier >= 4:
        for s in shadows:
            s.destroy()
            observer.add_satellite()
            bursts.append(Burst(s.x, s.y, (0,0,0)))
            if s.freq_key in chime_bank:
                ch = pygame.mixer.find_channel(True)
                if ch: ch.play(chime_bank[s.freq_key])
        shadows.clear()
    else:
        max_shadows = 8 + (tier * 6)
        spawn_rate = 0.01 + (total_prog * 0.02)

        if random.random() < spawn_rate and len(shadows) < max_shadows:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(1500, 3000)
            sx = observer.x + math.cos(angle) * dist
            sy = observer.y + math.sin(angle) * dist
            
            swarm_chance = min(0.9, 0.2 + (total_prog * 1.5))
            if random.random() < swarm_chance and len(shadows) <= (max_shadows - 4):
                base_f = round(random.uniform(1.5, 4.5), 1)
                offsets = [0.0, 0.05, -0.05, 0.1]
                for idx, off in enumerate(offsets):
                    open_ch = next((i for i in range(1, 28) if not any(s.channel_id == i for s in shadows)), None)
                    if open_ch:
                        f = round(base_f + off, 1)
                        pos_x = sx + math.cos(idx * 2.0) * 150
                        pos_y = sy + math.sin(idx * 2.0) * 150
                        shadows.append(Shadow(pos_x, pos_y, open_ch, forced_freq=f))
            else:
                open_ch = next((i for i in range(1, 28) if not any(s.channel_id == i for s in shadows)), None)
                if open_ch:
                    shadows.append(Shadow(sx, sy, open_ch))

    nearest_shadow = None
    min_dist_thread = float('inf')

    attraction_radius = 2000 + (total_prog * 10000)
    magnetic_power = 0.015 + (total_prog * 0.25)

    for s in shadows[:]:
        s.update(is_mirror=(tier == 3), target_vx=observer.vx, target_vy=observer.vy)
        
        dx = observer.x - s.x
        dy = observer.y - s.y
        dist = math.hypot(dx, dy)
        
        if dist > 12000:
            s.destroy()
            shadows.remove(s)
            continue

        freq_diff = abs(observer.phase_freq - s.freq)
        
        if dist < min_dist_thread:
            min_dist_thread = dist
            nearest_shadow = s

        if dist > 0 and dist < attraction_radius:
            resonance_threshold = 0.3 + (total_prog * 1.5)
            if freq_diff < resonance_threshold:
                pull = (magnetic_power * (1.0 - (freq_diff / resonance_threshold))) / max(1.0, dist * 0.001)
                s.vx += (dx / dist) * pull
                s.vy += (dy / dist) * pull

        collision_radius = (25 + observer.phase_amp) + (20 + s.amp)
        if dist < collision_radius:
            if freq_diff <= 0.2:
                s.integrated = True
                s.destroy()
                if s.freq_key in chime_bank:
                    ch_chime = pygame.mixer.find_channel(True)
                    if ch_chime: ch_chime.play(chime_bank[s.freq_key])
                
                observer.add_satellite()
                observer.total_consciousness = min(MAX_CONSCIOUSNESS, observer.total_consciousness + 50.0)
                bursts.append(Burst(s.x, s.y, freq_to_color(s.freq, tier, tier_prog)))
                shadows.remove(s)
                
            elif freq_diff > 1.2:
                s.integrated = True
                s.destroy()
                angle = math.atan2(observer.y - s.y, observer.x - s.x)
                observer.vx -= math.cos(angle) * 0.8
                observer.vy -= math.sin(angle) * 0.8
                observer.total_consciousness = max(0.0, observer.total_consciousness - 45.0)
                
                if observer.satellites:
                    sat = observer.satellites.pop()
                    sat.channel.stop()
                    
                bursts.append(Burst(s.x, s.y, (255, 50, 50)))
                shadows.remove(s)
            else:
                angle = math.atan2(s.y - observer.y, s.x - observer.x)
                s.vx += math.cos(angle) * 1.5
                s.vy += math.sin(angle) * 1.5

    for b in bursts[:]:
        b.update()
        if b.life <= 0: bursts.remove(b)

    observer.total_consciousness = max(0.0, observer.total_consciousness - 0.003)

    # --- RENDER ---
    cam_shake_x = 0
    cam_shake_y = 0
    if tier == 3:
        shake_intensity = tier_prog * 15.0
        cam_shake_x = random.uniform(-shake_intensity, shake_intensity)
        cam_shake_y = random.uniform(-shake_intensity, shake_intensity)
        
    cam_x = observer.x - WIDTH // 2 + cam_shake_x
    cam_y = observer.y - HEIGHT // 2 + cam_shake_y

    bardo.draw(screen, cam_x, cam_y, tier, tier_prog, total_prog, observer.space_rotation)

    if tier >= 4:
        draw_central_mandala(screen, WIDTH/2, HEIGHT/2, total_prog, observer.satellites, time_val, tier)

    if nearest_shadow and min_dist_thread < attraction_radius and tier < 4:
        corridor_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        p1 = (WIDTH // 2 + cam_shake_x, HEIGHT // 2 + cam_shake_y)
        p2 = (int(nearest_shadow.x - cam_x), int(nearest_shadow.y - cam_y))
        
        freq_diff = abs(observer.phase_freq - nearest_shadow.freq)
        resonance_factor = max(0.0, 1.0 - (freq_diff / 1.5))
        dx_c = p2[0] - p1[0]
        dy_c = p2[1] - p1[1]
        dist_pixels = math.hypot(dx_c, dy_c)
        
        guide_visibility = 1.0 - max(0.0, (total_prog - 0.6) * 2.5)
        if dist_pixels > 0 and guide_visibility > 0.01:
            steps = int(dist_pixels / 50)
            for step in range(1, steps):
                t = step / steps
                cx = p1[0] + dx_c * t
                cy = p1[1] + dy_c * t
                pulse = math.sin(time_val * 5.0 - step * 0.8)
                width = 80 * math.sin(t * math.pi) * resonance_factor
                alpha = int(30 * resonance_factor * guide_visibility * (1.0 + pulse*0.5))
                color = freq_to_color(nearest_shadow.freq, tier, tier_prog)
                pygame.draw.circle(corridor_surf, (*color[:3], alpha), (int(cx), int(cy)), int(max(5, width)))
        screen.blit(corridor_surf, (0, 0))

    for s in shadows:
        draw_chladni_entity(screen, s.x - cam_x, s.y - cam_y, s.freq, s.amp, time_val, tier, tier_prog)
        
    for b in bursts:
        b.draw(screen, cam_x, cam_y)
        
    for sat in observer.satellites:
        scale = 1.0 + max(0.0, (tier - 3) * tier_prog * 5.0)
        if tier >= 4:
            sat.draw(screen, WIDTH//2, HEIGHT//2, time_val, tier, tier_prog, scale=scale)
        else:
            sat.draw(screen, WIDTH//2 + cam_shake_x, HEIGHT//2 + cam_shake_y, time_val, tier, tier_prog)
        
    if tier < 4:
        draw_chladni_entity(screen, WIDTH//2 + cam_shake_x, HEIGHT//2 + cam_shake_y, observer.phase_freq, observer.phase_amp, time_val, tier, tier_prog, is_player=True)
        draw_central_mandala(screen, WIDTH, 0, total_prog, observer.satellites, time_val, tier)
        
    # Draw tactile input layer
    observer.draw_joystick(screen, tier, tier_prog)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

    # Ensure pygame quits cleanly on exit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()