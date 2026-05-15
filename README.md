# Setup
```bash
pip install numpy pyglet matplotlib
```
matplotlib is not necessary if not plotting

# Migration to Pyglet
[Pyglet Docs](https://pyglet.readthedocs.io/en/latest/index.html)

# To-do
- [x] Gravity on Earth
- [x] Build a 2d renderer based on Pyglet
  - [x] Implement multi-object rendering
  - [ ] Reuse old shapes
- [ ] Implement collisions
- [ ] Build a 3d renderer based on OpenGL
- [x] Springs
- [x] Diff eq. support
- [x] Two-body problems
  - [x] One fixed body
- [ ] N-body problems
  - [x] basic N-body problems
  - [ ] add functions to support moving center of mass
  - [ ] add functions to model changing mass overtime
  - [ ] energy support (to make it accurate to real life)
  - [x] Handle situations when bodies collied and distance b/w them is 0, so d^2(r)/dt^2 isn't NaN
- [ ] Particle simulation
- [ ] Fluid simulation

