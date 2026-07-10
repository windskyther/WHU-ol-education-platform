const projects = [
  {
    slug: "fan-study",
    letter: "F",
    name: "Fan Study",
    client: "Spotify for Artists",
    summary: "Audience intelligence for artists, labels, and managers.",
    colors: ["#F3A748", "#DB9338", "rgba(231,157,64,0.25)"],
  },
  {
    slug: "ikon-pass-destinations",
    letter: "I",
    name: "Ikon Pass Destinations",
    client: "Ikon Pass",
    summary: "A destination browser for resorts, maps, weather, and trip planning.",
    colors: ["#389CCA", "#2E82A8", "rgba(51,143,185,0.25)"],
  },
  {
    slug: "globekit",
    letter: "G",
    name: "GlobeKit",
    client: "Rivet Labs",
    summary: "A tactile showcase for interactive globes and geographic storytelling.",
    colors: ["#F5865E", "#E37A52", "rgba(236,128,88,0.25)"],
  },
  {
    slug: "ar-maps",
    letter: "I",
    name: "AR Maps",
    client: "Mountain Collective",
    summary: "Augmented wayfinding for trails, lifts, and terrain-aware navigation.",
    colors: ["#FCD259", "#E3BE4F", "rgba(240,200,84,0.25)"],
  },
  {
    slug: "experience-center",
    letter: "E",
    name: "Experience Center",
    client: "Toyota",
    summary: "A showroom interface for concept vehicles and immersive displays.",
    colors: ["#FE57E4", "#E34DCC", "rgba(241,82,216,0.25)"],
  },
  {
    slug: "in-car-navigation",
    letter: "I",
    name: "In-Car Navigation",
    client: "Mobility Lab",
    summary: "Route planning, terrain context, and driver-focused interface motion.",
    colors: ["#4264FB", "#3556E7", "rgba(60,93,241,0.25)"],
  },
  {
    slug: "tactical-mapping",
    letter: "T",
    name: "Tactical Mapping",
    client: "Field Systems",
    summary: "Dense geospatial tools for fast decisions in high-pressure contexts.",
    colors: ["#FF6152", "#D85144", "rgba(236,89,75,0.25)"],
  },
  {
    slug: "inside-design",
    letter: "I",
    name: "Inside Design",
    client: "InVision",
    summary: "Editorial systems, motion language, and a flexible publishing kit.",
    colors: ["#FF3366", "#D9204F", "rgba(236,42,91,0.25)"],
  },
  {
    slug: "chat",
    letter: "C",
    name: "Chat",
    client: "Social Platform",
    summary: "A quick, expressive conversation product with presence built in.",
    colors: ["#C5F22F", "#ACD035", "rgba(185,225,50,0.25)"],
  },
  {
    slug: "snkrs",
    letter: "S",
    name: "SNKRS",
    client: "Nike",
    summary: "Launch-day commerce with bold product storytelling and sharp pacing.",
    colors: ["#FF3C36", "#DF2924", "rgba(239,51,45,0.25)"],
  },
  {
    slug: "global-payments",
    letter: "G",
    name: "Global Payments",
    client: "Commerce Cloud",
    summary: "Transaction flows, merchant dashboards, and realtime financial maps.",
    colors: ["#1EA1F7", "#0F8ADB", "rgba(23,150,233,0.25)"],
  },
  {
    slug: "world-atlas",
    letter: "W",
    name: "World Atlas",
    client: "National Geographic",
    summary: "A living map experience for places, stories, and exploration.",
    colors: ["#FED737", "#E5C12C", "rgba(242,204,50,0.25)"],
  },
  {
    slug: "city-guides",
    letter: "C",
    name: "City Guides",
    client: "Travel Studio",
    summary: "Curated city pages with maps, lists, and location-first discovery.",
    colors: ["#E300F1", "#CA00D9", "rgba(215,0,229,0.25)"],
  },
  {
    slug: "national-parks",
    letter: "N",
    name: "National Parks",
    client: "Outdoor Archive",
    summary: "A park guide that blends planning tools with editorial scale.",
    colors: ["#FED737", "#E5C12C", "rgba(242,204,50,0.25)"],
  },
];

const root = document.documentElement;
const body = document.body;
const bullets = document.querySelector("#bullets");
const pages = document.querySelector("#pages");
const cursor = document.querySelector("#cursor");
const menuButton = document.querySelector("#menu-button");
const canvas = document.querySelector("#ribbon");
const ctx = canvas.getContext("2d");

let activeIndex = 0;
let mouseX = window.innerWidth / 2;
let mouseY = window.innerHeight / 2;
let cursorX = mouseX;
let cursorY = mouseY;
let scrollProgress = 0;
let scrollVelocity = 0;
let lastScrollY = window.scrollY;
let themePulse = 0;
let dpr = 1;
let ribbonNodes = [];

root.style.setProperty("--home-height", `${projects.length * 100}vh`);

function renderProjects() {
  bullets.innerHTML = projects
    .map(
      (project, index) => `
        <li class="${index === 0 ? "is-active" : ""}">
          <a href="#${project.slug}" data-index="${index}" aria-label="${project.name}">
            <span class="bullet-letter">${project.letter}</span>
            <span class="project-name">${project.name}</span>
          </a>
        </li>
      `,
    )
    .join("");

  pages.innerHTML = projects
    .map(
      (project, index) => `
        <li id="${project.slug}" class="page" data-index="${index}">
          <a href="#" aria-label="Open ${project.name}">
            <h2>${project.name}</h2>
            <h3>${project.client}</h3>
            <p>${project.summary}</p>
            <div class="arrow" aria-hidden="true">
              <div class="circle"></div>
              <div class="spine"></div>
            </div>
          </a>
        </li>
      `,
    )
    .join("");
}

function setTheme(index) {
  if (index === activeIndex && index !== 0) return;
  activeIndex = index;
  themePulse = 1;
  const [primary, secondary, selection] = projects[index].colors;
  root.style.setProperty("--highlight", primary);
  root.style.setProperty("--selection", selection);
  root.style.setProperty("--secondary", secondary);

  document.querySelectorAll("#bullets li").forEach((item, itemIndex) => {
    item.classList.toggle("is-active", itemIndex === index);
  });
  document.querySelectorAll("#pages .page").forEach((page, pageIndex) => {
    page.classList.toggle("is-active", pageIndex === index);
  });
}

function updateActiveFromScroll() {
  const projectHeight = window.innerHeight;
  const index = Math.max(0, Math.min(projects.length - 1, Math.round(window.scrollY / projectHeight)));
  scrollVelocity += (window.scrollY - lastScrollY) * 0.018;
  lastScrollY = window.scrollY;
  scrollProgress = window.scrollY / Math.max(1, document.body.scrollHeight - window.innerHeight);
  setTheme(index);
}

function initRibbon() {
  const nodeCount = Math.max(10, Math.ceil(window.innerHeight / 120) + 5);
  ribbonNodes = Array.from({ length: nodeCount }, (_, index) => {
    const progress = index / (nodeCount - 1);
    return {
      anchor: progress,
      x: window.innerWidth * 0.5,
      y: progress * window.innerHeight,
      vx: 0,
      vy: 0,
    };
  });
}

function resizeCanvas() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(window.innerWidth * dpr);
  canvas.height = Math.floor(window.innerHeight * dpr);
  canvas.style.width = `${window.innerWidth}px`;
  canvas.style.height = `${window.innerHeight}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  initRibbon();
}

function getRibbonPoint(index, offset) {
  const node = ribbonNodes[index];
  const previous = ribbonNodes[Math.max(0, index - 1)];
  const next = ribbonNodes[Math.min(ribbonNodes.length - 1, index + 1)];
  const tangentX = next.x - previous.x;
  const tangentY = next.y - previous.y;
  const length = Math.hypot(tangentX, tangentY) || 1;
  return {
    x: node.x + (-tangentY / length) * offset,
    y: node.y + (tangentX / length) * offset,
  };
}

function traceRibbonEdge(offset) {
  const first = getRibbonPoint(0, offset);
  ctx.moveTo(first.x, first.y);

  for (let index = 1; index < ribbonNodes.length; index += 1) {
    const previous = getRibbonPoint(index - 1, offset);
    const current = getRibbonPoint(index, offset);
    const cx = (previous.x + current.x) / 2;
    const cy = (previous.y + current.y) / 2;
    ctx.quadraticCurveTo(previous.x, previous.y, cx, cy);
  }

  const last = getRibbonPoint(ribbonNodes.length - 1, offset);
  ctx.lineTo(last.x, last.y);
}

function drawRibbonBand(width, fill, alpha) {
  ctx.beginPath();
  traceRibbonEdge(-width);
  for (let index = ribbonNodes.length - 1; index >= 0; index -= 1) {
    const previous = getRibbonPoint(Math.min(ribbonNodes.length - 1, index + 1), width);
    const current = getRibbonPoint(index, width);
    const cx = (previous.x + current.x) / 2;
    const cy = (previous.y + current.y) / 2;
    ctx.quadraticCurveTo(previous.x, previous.y, cx, cy);
  }
  ctx.closePath();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = fill;
  ctx.fill();
}

function drawRibbonSpine(offset, stroke, alpha, lineWidth) {
  ctx.beginPath();
  traceRibbonEdge(offset);
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = lineWidth;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.stroke();
}

function updateRibbonNodes(time) {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const mouseInfluenceX = mouseX / width - 0.5;
  const mouseInfluenceY = mouseY / height - 0.5;
  const activeBias = activeIndex / Math.max(1, projects.length - 1);
  const scrollPull = (scrollProgress - 0.5) * width * 0.22;
  const baseX = width * (0.46 + activeBias * 0.12) + scrollPull;
  const pulse = themePulse * 90;

  scrollVelocity *= 0.88;
  themePulse *= 0.93;

  ribbonNodes.forEach((node, index) => {
    const progress = node.anchor;
    const edgeWeight = Math.sin(progress * Math.PI);
    const phase = time * 0.0006 + progress * 6.8 + activeIndex * 0.42;
    const targetY =
      -height * 0.12 +
      progress * height * 1.24 +
      mouseInfluenceY * edgeWeight * 90 +
      scrollVelocity * edgeWeight * 26;
    const wave = Math.sin(phase) * 76 + Math.sin(phase * 1.62 + scrollProgress * 10) * 36;
    const targetX =
      baseX +
      wave * (0.5 + edgeWeight * 0.95) +
      mouseInfluenceX * edgeWeight * 240 +
      scrollVelocity * edgeWeight * 52 +
      Math.sin(progress * Math.PI * 2.4 + activeIndex) * pulse * edgeWeight;

    node.vx += (targetX - node.x) * 0.045;
    node.vy += (targetY - node.y) * 0.045;
    node.vx *= 0.78;
    node.vy *= 0.78;
    node.x += node.vx;
    node.y += node.vy;
  });
}

function drawRibbon(time) {
  const width = window.innerWidth;
  const height = window.innerHeight;
  const primary = getComputedStyle(root).getPropertyValue("--highlight").trim();
  const secondary = getComputedStyle(root).getPropertyValue("--secondary").trim() || primary;

  ctx.clearRect(0, 0, width, height);
  updateRibbonNodes(time);

  ctx.globalCompositeOperation = "source-over";

  const gradient = ctx.createLinearGradient(width * 0.28, 0, width * 0.72, height);
  gradient.addColorStop(0, primary);
  gradient.addColorStop(0.52, secondary);
  gradient.addColorStop(1, secondary);

  drawRibbonBand(58, gradient, 0.15);
  drawRibbonBand(26, gradient, 0.25);
  drawRibbonSpine(-72, gradient, 0.15, 3);
  drawRibbonSpine(72, gradient, 0.15, 3);
  drawRibbonSpine(0, gradient, 0.34, 5);

  ribbonNodes.forEach((node, index) => {
    if (index % 2 !== 0) return;
    ctx.beginPath();
    ctx.arc(node.x, node.y, 2.3, 0, Math.PI * 2);
    ctx.globalAlpha = 0.18;
    ctx.fillStyle = primary;
    ctx.fill();
  });

  ctx.globalAlpha = 1;
}

function animate(time) {
  cursorX += (mouseX - cursorX) * 0.22;
  cursorY += (mouseY - cursorY) * 0.22;
  cursor.style.left = `${cursorX}px`;
  cursor.style.top = `${cursorY}px`;
  drawRibbon(time);
  requestAnimationFrame(animate);
}

renderProjects();
setTheme(0);
resizeCanvas();
updateActiveFromScroll();
requestAnimationFrame(animate);

window.addEventListener("scroll", updateActiveFromScroll, { passive: true });
window.addEventListener("resize", () => {
  resizeCanvas();
  updateActiveFromScroll();
});

window.addEventListener("pointermove", (event) => {
  mouseX = event.clientX;
  mouseY = event.clientY;
});

document.querySelectorAll("a, button").forEach((element) => {
  element.addEventListener("pointerenter", () => cursor.classList.add("is-active"));
  element.addEventListener("pointerleave", () => cursor.classList.remove("is-active"));
});

bullets.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-index]");
  if (!link) return;
  event.preventDefault();
  const index = Number(link.dataset.index);
  window.scrollTo({
    top: index * window.innerHeight,
    behavior: "smooth",
  });
});

pages.addEventListener("click", (event) => {
  const link = event.target.closest(".page a");
  if (link) event.preventDefault();
});

menuButton.addEventListener("click", () => {
  const isOpen = body.classList.toggle("menu-open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
});

document.querySelectorAll("#menu a").forEach((link) => {
  link.addEventListener("click", () => {
    body.classList.remove("menu-open");
    menuButton.setAttribute("aria-expanded", "false");
  });
});
