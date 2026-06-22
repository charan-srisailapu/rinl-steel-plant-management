import { useEffect, useRef } from 'react'

const COLORS = ['#ec6a06', '#ffb690', '#ffdbca']

class Particle {
  constructor(w, h) {
    this.w = w; this.h = h
    this.reset()
  }
  reset() {
    this.x = Math.random() * this.w
    this.y = this.h + Math.random() * 100
    this.size = Math.random() * 2.5 + 0.5
    this.speedY = Math.random() * 1.5 + 0.5
    this.speedX = (Math.random() - 0.5) * 0.5
    this.opacity = Math.random() * 0.8 + 0.2
    this.color = COLORS[Math.floor(Math.random() * COLORS.length)]
    this.osc = Math.random() * Math.PI * 2
    this.oscSpeed = Math.random() * 0.05 + 0.01
  }
  update() {
    this.y -= this.speedY
    this.osc += this.oscSpeed
    this.x += this.speedX + Math.sin(this.osc) * 0.5
    if (this.y < -10) this.reset()
  }
  draw(ctx) {
    ctx.globalAlpha = this.opacity
    ctx.fillStyle = this.color
    ctx.shadowBlur = this.size * 2
    ctx.shadowColor = this.color
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
    ctx.shadowBlur = 0
  }
}

export default function EmberEffect() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let particles = []
    let animId

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    const count = Math.min(Math.floor(window.innerWidth / 10), 120)
    particles = Array.from({ length: count }, () => new Particle(canvas.width, canvas.height))

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      particles.forEach(p => { p.update(); p.draw(ctx) })
      animId = requestAnimationFrame(animate)
    }
    animate()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute', inset: 0, zIndex: 5, pointerEvents: 'none',
      }}
    />
  )
}
