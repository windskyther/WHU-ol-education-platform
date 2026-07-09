<template>
  <canvas ref="canvasRef" class="rally-ribbon" aria-hidden="true"></canvas>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const canvasRef = ref(null)
let ctx
let frameId = 0
let dpr = 1
let mouseX = 0
let mouseY = 0
let nodes = []
let scrollProgress = 0
let lastScrollY = 0
let scrollVelocity = 0

const palette = ['#f3a748', '#2d8cca', '#ff4fd8', '#c8f23a', '#4264fb', '#ff5a4d']

function initNodes() {
  const count = Math.max(10, Math.ceil(window.innerHeight / 120) + 4)
  nodes = Array.from({ length: count }, (_, index) => {
    const anchor = index / (count - 1)
    return {
      anchor,
      x: window.innerWidth * 0.55,
      y: anchor * window.innerHeight,
      vx: 0,
      vy: 0
    }
  })
}

function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvas.width = Math.floor(window.innerWidth * dpr)
  canvas.height = Math.floor(window.innerHeight * dpr)
  canvas.style.width = `${window.innerWidth}px`
  canvas.style.height = `${window.innerHeight}px`
  ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  initNodes()
}

function updateScroll() {
  const maxScroll = Math.max(1, document.body.scrollHeight - window.innerHeight)
  scrollVelocity += (window.scrollY - lastScrollY) * 0.018
  lastScrollY = window.scrollY
  scrollProgress = window.scrollY / maxScroll
}

function point(index, offset) {
  const node = nodes[index]
  const previous = nodes[Math.max(0, index - 1)]
  const next = nodes[Math.min(nodes.length - 1, index + 1)]
  const tangentX = next.x - previous.x
  const tangentY = next.y - previous.y
  const length = Math.hypot(tangentX, tangentY) || 1
  return {
    x: node.x + (-tangentY / length) * offset,
    y: node.y + (tangentX / length) * offset
  }
}

function trace(offset) {
  const first = point(0, offset)
  ctx.moveTo(first.x, first.y)
  for (let index = 1; index < nodes.length; index += 1) {
    const prev = point(index - 1, offset)
    const current = point(index, offset)
    ctx.quadraticCurveTo(prev.x, prev.y, (prev.x + current.x) / 2, (prev.y + current.y) / 2)
  }
}

function drawBand(width, fill, alpha) {
  ctx.beginPath()
  trace(-width)
  for (let index = nodes.length - 1; index >= 0; index -= 1) {
    const prev = point(Math.min(nodes.length - 1, index + 1), width)
    const current = point(index, width)
    ctx.quadraticCurveTo(prev.x, prev.y, (prev.x + current.x) / 2, (prev.y + current.y) / 2)
  }
  ctx.closePath()
  ctx.globalAlpha = alpha
  ctx.fillStyle = fill
  ctx.fill()
}

function drawSpine(offset, stroke, alpha, width) {
  ctx.beginPath()
  trace(offset)
  ctx.globalAlpha = alpha
  ctx.strokeStyle = stroke
  ctx.lineWidth = width
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.stroke()
}

function updateNodes(time) {
  const width = window.innerWidth
  const height = window.innerHeight
  const mouseBiasX = mouseX / Math.max(width, 1) - 0.5
  const mouseBiasY = mouseY / Math.max(height, 1) - 0.5
  const baseX = width * (0.48 + scrollProgress * 0.18)
  scrollVelocity *= 0.88

  nodes.forEach((node) => {
    const progress = node.anchor
    const edge = Math.sin(progress * Math.PI)
    const phase = time * 0.00062 + progress * 7.2 + scrollProgress * 8
    const targetX = baseX + Math.sin(phase) * 120 * (0.45 + edge) + mouseBiasX * edge * 220 + scrollVelocity * edge * 34
    const targetY = -height * 0.12 + progress * height * 1.24 + mouseBiasY * edge * 86

    node.vx += (targetX - node.x) * 0.045
    node.vy += (targetY - node.y) * 0.045
    node.vx *= 0.78
    node.vy *= 0.78
    node.x += node.vx
    node.y += node.vy
  })
}

function draw(time) {
  if (!ctx) return
  const width = window.innerWidth
  const height = window.innerHeight
  updateNodes(time)
  ctx.clearRect(0, 0, width, height)

  const colorA = palette[Math.floor(scrollProgress * palette.length) % palette.length]
  const colorB = palette[(Math.floor(scrollProgress * palette.length) + 2) % palette.length]
  const gradient = ctx.createLinearGradient(width * 0.28, 0, width * 0.76, height)
  gradient.addColorStop(0, colorA)
  gradient.addColorStop(0.55, colorB)
  gradient.addColorStop(1, colorA)

  drawBand(70, gradient, 0.12)
  drawBand(30, gradient, 0.24)
  drawSpine(-78, gradient, 0.12, 3)
  drawSpine(78, gradient, 0.12, 3)
  drawSpine(0, gradient, 0.32, 5)

  ctx.globalAlpha = 1
  frameId = requestAnimationFrame(draw)
}

function handlePointerMove(event) {
  mouseX = event.clientX
  mouseY = event.clientY
}

onMounted(() => {
  mouseX = window.innerWidth / 2
  mouseY = window.innerHeight / 2
  lastScrollY = window.scrollY
  resize()
  updateScroll()
  frameId = requestAnimationFrame(draw)
  window.addEventListener('resize', resize)
  window.addEventListener('scroll', updateScroll, { passive: true })
  window.addEventListener('pointermove', handlePointerMove)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  window.removeEventListener('resize', resize)
  window.removeEventListener('scroll', updateScroll)
  window.removeEventListener('pointermove', handlePointerMove)
})
</script>

<style scoped>
.rally-ribbon {
  position: fixed;
  inset: 0;
  z-index: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
}
</style>
