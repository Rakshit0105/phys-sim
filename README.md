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
  - [ ] Implement proper energy conservation during different types of collisions
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

Switched from RK4 to velocity verlet for significant performance gains, and energy+momentum conservation. Look more into symplectic integrators, and hamiltonian
