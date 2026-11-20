# linux-20-runners
Public repo - 20 parallel Linux devices for any render work.
Any render work uses ALL 20 devices, never 1 device alone. The render is split into 20 chunks, one per device, all 20 run at the same time.
Devices (public repo, GitHub Actions standard runners): Linux ubuntu-latest, 4 vCPU, 16 GB RAM, 14 GB SSD, no GPU - CPU render only, free and unlimited in a public repo, max 20 parallel jobs on Free, max 6 hours per job.
How to run: put your .blend file in the repo e.g. renders/scene.blend, go to Actions - 20 Linux Render - Run workflow, set blend_file, total_frames (e.g. 200), output_dir. Device 1 renders frames 1-10, device 2 renders 11-20, ... device 20 renders 191-200. Each device uploads its frames as an artifact frames-device-N-start-end.
Files: .github/workflows/20-linux-render.yml, scripts/split_frames.py.
Limits: CPU only, keep .blend + textures under 14 GB disk, keep each chunk under 6 hours, artifacts kept 7 days.
