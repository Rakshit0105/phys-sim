# Setup
```bash
pip install numpy pyglet matplotlib panda3d
```
matplotlib is not necessary if not plotting

# Note:
new_energy_n_body.py and n_body.py are the only ones that will currently run due to changes made to rendering. Other files haven't been updated with the new syntax yet.

# To-do
- [x] Gravity on Earth
- [x] Build a 2d renderer based on Pyglet
  - [x] Implement multi-object rendering
  - [ ] Reuse old shapes
- [ ] Implement collisions
  - [ ] Come up with different models for bodies colliding
  - [ ] Supoort for different types of collisions (and respective energy+momentum changes)
- [ ] Build a 3d renderer based on Panda3D
- [x] Springs
- [x] Diff eq. support
- [x] Two-body problems
  - [x] One fixed body
- [ ] N-body problems
  - [x] basic N-body problems
  - [ ] add functions to support moving center of mass
  - [ ] add functions to model changing mass overtime
  - [x] energy support (to make it accurate to real life)
- [ ] Particle simulation
- [ ] Fluid simulation

Switched from RK4 to velocity verlet for significant performance gains, and energy+momentum conservation. 

# Example System
Energy and momentum graphs for an 11 body gravitational system with velocity verlet (time step = 0.05):
Total energy = -6819.154250916657
[[./velocity_verlet_11_body_energy.png]]

Zoomed in energy plot
[[./velocity_verlet_11_body_energy_zoomed.png]]

<p_x, p_y, p_z> represent each of the 3 lines. Total momentum = <-0.0064815, 0.009429, 0.>
[[./velocity_verlet_11_body_momentum.png]]
