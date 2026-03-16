"""Import and plot SDFast sphere results"""

# Python standard packages (comes with Python)
import sys

# Open Source Python Imports (from pip/miniforge conda, etc.)
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation

# Note: This also uses the ffmpeg back-end to produce the .mp4
#       animation, so that will need to be installed in the
#       environment as well.

# Local Organization Imports
# None

# Local Project Imports
# None

# grab program name from command line
data_fname = sys.argv[1]
exe_name = data_fname.split(".")[0]

# Ingest data using a CSV reader set to a white space separator,
# skipping first row of captured STDOUT and using the second row
# as the header column and the first column as the index.
data = pd.read_csv(
    f"{data_fname}",
    sep="\s+",  ## replaces deprecated delim_whitespace=True
    skiprows=7,
    header=0,
    index_col=1,
)

print('Loaded this data:')
print(data)

print('Plotting trajectory of center of ball vs. time')

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Map condition column to colors (strip leading * from transition markers)
cond_color_map = {'FREE': 'yellow', 'ROLL': 'lightblue', 'SLIP': 'lightcoral'}
cond_stripped = data['cond'].str.strip().str.lstrip('*')

# Add colored background regions to all subplots
times = data.index.values.astype(float)
for ax in [ax1, ax2, ax3]:
    # Find contiguous regions with the same condition
    current_cond = cond_stripped.iloc[0]
    start_time = times[0]

    for i in range(1, len(cond_stripped)):
        if cond_stripped.iloc[i] != current_cond:
            # End of current region, draw background
            ax.axvspan(start_time, times[i-1],
                      facecolor=cond_color_map.get(current_cond, 'white'),
                      alpha=0.3, zorder=0)
            # Start new region
            current_cond = cond_stripped.iloc[i]
            start_time = times[i]

    # Draw final region
    ax.axvspan(start_time, times[-1],
              facecolor=cond_color_map.get(current_cond, 'white'),
              alpha=0.3, zorder=0)

# Plot the data
data.loc[:,'com_x':'com_z'].plot(ax=ax1, marker='.')
ax1.set_ylabel('Position (m)')
ax1.set_title('Center of Mass Position vs Time')
ax1.grid()

data['energy'].plot(ax=ax2, marker='.', color='purple')
ax2.set_ylabel('Energy (J)')
ax2.set_title('Total Energy vs Time')
ax2.grid()

data.loc[:,'angv_1':'angv_3'].plot(ax=ax3, marker='.')
ax3.set_ylabel('Angular Velocity (rad/s)')
ax3.set_xlabel('Time (s)')
ax3.set_title('Rotational Rates vs Time')
ax3.grid()

fig.tight_layout()
fig.savefig('sphere_center_vs_time.pdf')

print('Plotting trajectory of center of ball in 3D')

# 3D position plot of ball inside spherical surface
fig3d = plt.figure()
ax3d = fig3d.add_subplot(111, projection='3d')

# Plot ball trajectory (x=horizontal, z=horizontal, y=up)
ax3d.plot(data['com_x'], data['com_z'], data['com_y'], linewidth=0.5)

# Draw the outer spherical surface (radius = outer - inner = 1m constraint surface)
u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
r_surface = 1.0  # constraint surface radius (outer 2m - inner 1m ball)
xs = r_surface * np.outer(np.cos(u), np.sin(v))
zs = r_surface * np.outer(np.sin(u), np.sin(v))
ys = r_surface * np.outer(np.ones(np.size(u)), np.cos(v))
ax3d.plot_surface(xs, zs, ys, alpha=0.1, color='gray')

ax3d.set_xlabel('X')
ax3d.set_zlabel('Y (up)')
ax3d.set_ylabel('Z')
ax3d.set_title('Ball CoM Position Inside Spherical Surface')
ax3d.set_aspect('equal')
fig3d.savefig('sphere_center_3d_position.pdf')

# --- Animate the inner ball rolling inside the spherical surface ---

print('Animating the simulated ball inside a sphere...')

# Integrate angular velocity to get orientation at each timestep.
# angv_1, angv_2, angv_3 are body-frame angular velocities (rad/s).
times = data.index.values.astype(float)
omega = data[['angv_1', 'angv_2', 'angv_3']].values
pos = data[['com_x', 'com_y', 'com_z']].values

# Map condition column to colors (strip leading * from transition markers)
cond_color_map = {'FREE': 'green', 'ROLL': 'blue', 'SLIP': 'red'}
cond_stripped = data['cond'].str.strip().str.lstrip('*')
seg_colors = cond_stripped.map(cond_color_map).values

# Build rotation matrices by integrating angular velocity via quaternions
quats = np.zeros((len(times), 4))  # [x, y, z, w] scipy convention
quats[0] = [0, 0, 0, 1]  # identity
for i in range(1, len(times)):
    dt = times[i] - times[i - 1]
    # Average angular velocity over the interval
    w = 0.5 * (omega[i - 1] + omega[i])
    angle = np.linalg.norm(w) * dt
    if angle > 1e-12:
        axis = w / np.linalg.norm(w)
        dR = Rotation.from_rotvec(axis * angle)
    else:
        dR = Rotation.identity()
    R_prev = Rotation.from_quat(quats[i - 1])
    R_new = R_prev * dR  # body-frame rotation update
    quats[i] = R_new.as_quat()

# Generate outer sphere mesh at true radius 2.0 for animation
r_outer = 2.0
u_outer = np.linspace(0, 2 * np.pi, 50)
v_outer = np.linspace(0, np.pi, 50)
xs_outer = r_outer * np.outer(np.cos(u_outer), np.sin(v_outer))
zs_outer = r_outer * np.outer(np.sin(u_outer), np.sin(v_outer))
ys_outer = r_outer * np.outer(np.ones(np.size(u_outer)), np.cos(v_outer))

# Generate reference points on the ball surface (latitude/longitude grid)
r_ball = 1.0
n_lon, n_lat = 12, 7
phi_ref = np.linspace(0, 2 * np.pi, n_lon, endpoint=False)
theta_ref = np.linspace(np.pi / 8, 7 * np.pi / 8, n_lat)

# Build latitude circles (connected rings at each theta)
lat_circles_body = []
for th in theta_ref:
    circ = r_ball * np.column_stack([
        np.sin(th) * np.cos(np.linspace(0, 2 * np.pi, n_lon + 1)),
        np.sin(th) * np.sin(np.linspace(0, 2 * np.pi, n_lon + 1)),
        np.full(n_lon + 1, np.cos(th)),
    ])
    lat_circles_body.append(circ)

# Build longitude lines (connected arcs at each phi)
lon_lines_body = []
for ph in phi_ref:
    arc = r_ball * np.column_stack([
        np.sin(theta_ref) * np.cos(ph),
        np.sin(theta_ref) * np.sin(ph),
        np.cos(theta_ref),
    ])
    lon_lines_body.append(arc)

# Wireframe circles for the ball: 3 great circles in body frame
n_circle = 60
circ_angle = np.linspace(0, 2 * np.pi, n_circle)
great_circles_body = []
# XY plane circle
great_circles_body.append(r_ball * np.column_stack([
    np.cos(circ_angle), np.sin(circ_angle), np.zeros(n_circle)]))
# XZ plane circle
great_circles_body.append(r_ball * np.column_stack([
    np.cos(circ_angle), np.zeros(n_circle), np.sin(circ_angle)]))
# YZ plane circle
great_circles_body.append(r_ball * np.column_stack([
    np.zeros(n_circle), np.cos(circ_angle), np.sin(circ_angle)]))

# Set up animation figure
fig_anim = plt.figure(figsize=(8, 8))
ax_anim = fig_anim.add_subplot(111, projection='3d')

# Subsample frames for reasonable animation speed
step = max(1, len(times) // 200)
frame_indices = list(range(0, len(times), step))


def update(frame_idx):
    ax_anim.cla()

    # Outer spherical surface at radius 2.0 (translucent)
    ax_anim.plot_surface(xs_outer, zs_outer, ys_outer, alpha=0.08, color='gray')

    # Trajectory trace up to current time, colored by condition
    for j in range(1, frame_idx + 1):
        ax_anim.plot(pos[j - 1:j + 1, 0], pos[j - 1:j + 1, 2],
                     pos[j - 1:j + 1, 1], color=seg_colors[j],
                     linewidth=0.8, alpha=0.5)

    # Current ball position (x, z horizontal; y up)
    cx, cy, cz = pos[frame_idx]
    R = Rotation.from_quat(quats[frame_idx]).as_matrix()

    # Draw great circles rotated to current orientation and translated
    colors = ['red', 'green', 'blue']
    for gc_body, color in zip(great_circles_body, colors):
        gc_world = (R @ gc_body.T).T
        # Remap: data x -> plot x, data z -> plot y, data y -> plot z (up)
        ax_anim.plot(gc_world[:, 0] + cx,
                     gc_world[:, 2] + cz,
                     gc_world[:, 1] + cy,
                     color=color, linewidth=0.8, alpha=0.6)

    # Draw connected latitude circles on ball surface
    for lc_body in lat_circles_body:
        lc_world = (R @ lc_body.T).T
        ax_anim.plot(lc_world[:, 0] + cx, lc_world[:, 2] + cz,
                     lc_world[:, 1] + cy,
                     color='black', linewidth=0.5, alpha=0.4)

    # Draw connected longitude lines on ball surface
    for ll_body in lon_lines_body:
        ll_world = (R @ ll_body.T).T
        ax_anim.plot(ll_world[:, 0] + cx, ll_world[:, 2] + cz,
                     ll_world[:, 1] + cy,
                     color='black', linewidth=0.5, alpha=0.4)

    # Ball center marker
    ax_anim.scatter([cx], [cz], [cy], c='blue', s=20)

    # Formatting
    lim = 2.5
    ax_anim.set_xlim(-lim, lim)
    ax_anim.set_ylim(-lim, lim)
    ax_anim.set_zlim(-lim, lim)
    ax_anim.set_xlabel('X')
    ax_anim.set_ylabel('Z')
    ax_anim.set_zlabel('Y (up)')
    ax_anim.set_title(f'Ball Rolling in Sphere  t={times[frame_idx]:.3f}s')
    ax_anim.set_aspect('equal')


anim = FuncAnimation(fig_anim, update, frames=frame_indices,
                     interval=50, repeat=True)
anim.save('sphere_animation.mp4', writer='ffmpeg', fps=30, dpi=150)
print('Animation saved to sphere_animation.mp4')
