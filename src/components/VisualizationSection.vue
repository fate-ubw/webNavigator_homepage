<script setup>
import { ref, onMounted, shallowRef, reactive, computed, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

// Trajectory player state
const TRAJECTORY_PATH = '/webarena-760'
const trajectoryData = ref(null)
const totalSteps = computed(() => trajectoryData.value?.trajectory?.length || 0)
const isPlaying = ref(false)
const currentStep = ref(0)
let playInterval = null

const currentUrl = computed(() => {
  if (!trajectoryData.value || currentStep.value >= totalSteps.value) return ''
  const url = trajectoryData.value.trajectory[currentStep.value].url
  // Truncate long URLs
  if (url.length > 60) {
    try {
      const urlObj = new URL(url)
      const fullPath = urlObj.pathname + urlObj.search + urlObj.hash
      if (fullPath.length > 45) {
        return urlObj.origin + fullPath.substring(0, 45) + '...'
      }
      return url
    } catch {
      return url.substring(0, 60) + '...'
    }
  }
  return url
})

const currentScreenshot = computed(() => {
  return `${TRAJECTORY_PATH}/step${currentStep.value}.png`
})

const togglePlay = () => {
  isPlaying.value = !isPlaying.value
}

const goToStep = (step) => {
  currentStep.value = Math.max(0, Math.min(step, totalSteps.value - 1))
}

const nextStep = () => {
  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++
  } else {
    isPlaying.value = false
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// Domain to tab mapping
const domainToTab = {
  'shopping_admin': 'admin',
  'map': 'map',
  'gitlab': 'gitlab',
  'shopping': 'shopping',
  'postmill': 'postmill'
}

// Cache for highlighted node images (pre-generated red border versions)
const highlightedImageCache = reactive({})

// Track current highlight target (the node that should be red)
const currentHighlightTarget = ref(null) // { tabId, targetPage, nodeId }

// Track which node is currently highlighted (for restoration)
const currentHighlightedNode = ref(null) // { nodeId, originalSymbol, originalSize }

// Track transition animation
let transitionAnimationId = null
const transitionProgress = ref(0) // 0-1, for color interpolation

// Overlay state for "Retrieving and Navigating..." message
const showNavigatingOverlay = ref(false)

// Callback to advance to next step after transition completes
let onTransitionComplete = null

// Pre-generate highlighted images for all target_pages in trajectory
const preloadHighlightedImages = async () => {
  if (!trajectoryData.value) return
  
  const targetPages = trajectoryData.value.trajectory
    .filter(step => step.target_page && step.navigate_domain)
    .map(step => ({
      targetPage: step.target_page,
      tabId: domainToTab[step.navigate_domain]
    }))
  
  for (const { targetPage, tabId } of targetPages) {
    const graphPath = GRAPH_TABS.find(t => t.id === tabId)?.path
    if (!graphPath) continue
    
    const cacheKey = `${tabId}_${targetPage}`
    if (highlightedImageCache[cacheKey]) continue
    
    const imagePath = `${graphPath}/screenshots_cropped_resized/${targetPage}`
    const highlightedImage = await createBorderedImage(imagePath, '#ef4444', 6)
    highlightedImageCache[cacheKey] = highlightedImage
  }
}

// Stop transition animation
const stopTransitionAnimation = () => {
  if (transitionAnimationId) {
    cancelAnimationFrame(transitionAnimationId)
    transitionAnimationId = null
  }
}

// Remove current highlight (restore original appearance)
const removeHighlight = () => {
  stopFollowingNode()
  stopTransitionAnimation()
  
  if (!currentHighlightedNode.value || !chartInstance) return
  
  const { nodeId, originalSymbol, originalSize } = currentHighlightedNode.value
  
  const option = chartInstance.getOption()
  if (!option?.series?.[0]?.data) return
  
  const nodeIndex = option.series[0].data.findIndex(n => n.id === nodeId)
  if (nodeIndex === -1) return
  
  const node = option.series[0].data[nodeIndex]
  node.symbol = originalSymbol
  node.symbolSize = originalSize
  node.z = 0
  
  chartInstance.setOption({ series: [{ data: option.series[0].data }] }, false)
  currentHighlightedNode.value = null
  currentHighlightTarget.value = null
  transitionProgress.value = 0
}

// Apply full highlight (red border) immediately
const applyFullHighlight = (tabId, targetPage, shouldFollow = true) => {
  if (!chartInstance) return
  
  const graphData = graphDataMap[tabId]
  if (!graphData) return
  
  // Find node by screen_path
  const nodeEntry = Object.entries(graphData.nodes).find(([id, node]) => 
    node.screen_path === targetPage
  )
  if (!nodeEntry) return
  
  const [nodeId] = nodeEntry
  const cacheKey = `${tabId}_${targetPage}`
  const highlightedImage = highlightedImageCache[cacheKey]
  if (!highlightedImage) return
  
  const option = chartInstance.getOption()
  if (!option?.series?.[0]?.data) return
  
  const nodeIndex = option.series[0].data.findIndex(n => n.id === nodeId)
  if (nodeIndex === -1) return
  
  const node = option.series[0].data[nodeIndex]
  
  // Store original for restoration
  currentHighlightedNode.value = {
    nodeId,
    originalSymbol: node.symbol,
    originalSize: [...node.symbolSize]
  }
  
  currentHighlightTarget.value = { tabId, targetPage, nodeId }
  transitionProgress.value = 1
  
  // Apply highlight
  node.symbol = `image://${highlightedImage}`
  node.symbolSize = [128 + 12, 72 + 12]
  node.z = 100
  
  chartInstance.setOption({ series: [{ data: option.series[0].data }] }, false)
  
  // Start following the node (only if requested)
  if (shouldFollow) {
    startFollowingNode(nodeId)
  }
}

// Start gradual transition to red (during playback)
const startHighlightTransition = (tabId, targetPage) => {
  if (!chartInstance) return
  
  const graphData = graphDataMap[tabId]
  if (!graphData) return
  
  // Find node by screen_path
  const nodeEntry = Object.entries(graphData.nodes).find(([id, node]) => 
    node.screen_path === targetPage
  )
  if (!nodeEntry) return
  
  const [nodeId] = nodeEntry
  const graphPath = GRAPH_TABS.find(t => t.id === tabId)?.path
  if (!graphPath) return
  
  const option = chartInstance.getOption()
  if (!option?.series?.[0]?.data) return
  
  const nodeIndex = option.series[0].data.findIndex(n => n.id === nodeId)
  if (nodeIndex === -1) return
  
  const node = option.series[0].data[nodeIndex]
  
  // Store original for restoration (if not already stored)
  if (!currentHighlightedNode.value || currentHighlightedNode.value.nodeId !== nodeId) {
    currentHighlightedNode.value = {
      nodeId,
      originalSymbol: node.symbol,
      originalSize: [...node.symbolSize]
    }
  }
  
  currentHighlightTarget.value = { tabId, targetPage, nodeId }
  transitionProgress.value = 0
  
  // Show overlay
  showNavigatingOverlay.value = true
  
  // Start following the node
  startFollowingNode(nodeId)
  
  // Animate the transition over 2 seconds (playback interval)
  const duration = 3000
  const startTime = performance.now()
  const originalNodeData = graphDataMap[tabId].nodes[nodeId]
  const isRootNode = originalNodeData.screen_path.includes('start')
  let originalBorderColor = '#3b82f6'
  if (!isRootNode) {
    originalBorderColor = originalNodeData.can_arrival_directly ? '#10b981' : '#f59e0b'
  }
  
  const animate = async (currentTime) => {
    if (!currentHighlightTarget.value || currentHighlightTarget.value.nodeId !== nodeId) {
      showNavigatingOverlay.value = false
      return
    }
    
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    transitionProgress.value = progress
    
    // Interpolate color from original to red
    const r1 = parseInt(originalBorderColor.slice(1, 3), 16)
    const g1 = parseInt(originalBorderColor.slice(3, 5), 16)
    const b1 = parseInt(originalBorderColor.slice(5, 7), 16)
    const r2 = 239, g2 = 68, b2 = 68 // #ef4444
    
    const r = Math.round(r1 + (r2 - r1) * progress)
    const g = Math.round(g1 + (g2 - g1) * progress)
    const b = Math.round(b1 + (b2 - b1) * progress)
    const currentColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
    
    // Interpolate border width
    const originalWidth = isRootNode ? 4 : 3
    const targetWidth = 6
    const currentWidth = originalWidth + (targetWidth - originalWidth) * progress
    
    // Create bordered image with current color
    const imagePath = `${graphPath}/screenshots_cropped_resized/${targetPage}`
    const borderedImage = await createBorderedImage(imagePath, currentColor, currentWidth)
    
    // Update node
    const currentOption = chartInstance.getOption()
    if (!currentOption?.series?.[0]?.data) return
    
    const currentNodeIndex = currentOption.series[0].data.findIndex(n => n.id === nodeId)
    if (currentNodeIndex === -1) return
    
    const currentNode = currentOption.series[0].data[currentNodeIndex]
    currentNode.symbol = `image://${borderedImage}`
    currentNode.symbolSize = [128 + currentWidth * 2, 72 + currentWidth * 2]
    currentNode.z = 100
    
    chartInstance.setOption({ series: [{ data: currentOption.series[0].data }] }, false)
    
    if (progress < 1 && isPlaying.value) {
      transitionAnimationId = requestAnimationFrame(animate)
    } else if (progress >= 1) {
      // Animation complete, hide overlay and trigger callback
      showNavigatingOverlay.value = false
      if (onTransitionComplete) {
        const callback = onTransitionComplete
        onTransitionComplete = null
        callback()
      }
    }
  }
  
  transitionAnimationId = requestAnimationFrame(animate)
}

// Check if previous step has target_page pointing to current step's page
const getPreviousStepTarget = (step) => {
  if (step <= 0 || !trajectoryData.value) return null
  
  const prevStep = trajectoryData.value.trajectory[step - 1]
  if (prevStep.target_page && prevStep.navigate_domain) {
    return {
      tabId: domainToTab[prevStep.navigate_domain],
      targetPage: prevStep.target_page
    }
  }
  return null
}

// Handle step change
const handleStepChange = async (step) => {
  if (!trajectoryData.value || step >= totalSteps.value) return
  
  const stepData = trajectoryData.value.trajectory[step]
  const prevTarget = getPreviousStepTarget(step)
  
  // Remove any existing highlight first
  removeHighlight()
  
  // Check if previous step had a target_page (meaning this step should show the red node)
  if (prevTarget) {
    const { tabId, targetPage } = prevTarget
    
    // Switch tab if needed
    if (activeTab.value !== tabId) {
      await switchTab(tabId)
    }
    
    // Apply full highlight immediately (we're at the destination step)
    applyFullHighlight(tabId, targetPage)
  }
  // Check if current step has target_page (meaning next step will show the red node)
  else if (stepData.target_page && stepData.navigate_domain && isPlaying.value) {
    const tabId = domainToTab[stepData.navigate_domain]
    
    // Switch tab if needed
    if (activeTab.value !== tabId) {
      await switchTab(tabId)
    }
    
    // Start gradual transition (only during playback)
    startHighlightTransition(tabId, stepData.target_page)
  }
}

// Track the follow animation frame
let followAnimationId = null

// Stop following node
const stopFollowingNode = () => {
  if (followAnimationId) {
    cancelAnimationFrame(followAnimationId)
    followAnimationId = null
  }
}

// Continuously follow highlighted node until layout stabilizes
const startFollowingNode = (nodeId) => {
  // Stop any previous following
  stopFollowingNode()
  
  if (!chartInstance) return
  
  let lastNodeX = null
  let lastNodeY = null
  let stableCount = 0
  const stableThreshold = 30 // ~0.5s at 60fps
  
  // Smoothing factor (0-1, lower = smoother but slower)
  const smoothFactor = 0.15
  
  const follow = () => {
    if (!chartInstance || !currentHighlightTarget.value) {
      stopFollowingNode()
      return
    }
    
    // Get the graph series model to access layout data
    const model = chartInstance.getModel()
    if (!model) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const seriesModel = model.getSeriesByIndex(0)
    if (!seriesModel) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const graph = seriesModel.getGraph()
    if (!graph) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const graphNode = graph.getNodeById(nodeId)
    if (!graphNode) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const layout = graphNode.getLayout()
    if (!layout || layout[0] === undefined || layout[1] === undefined) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const [nodeX, nodeY] = layout
    
    // Use convertToPixel to get actual pixel position
    const pixelPos = chartInstance.convertToPixel({ seriesIndex: 0 }, [nodeX, nodeY])
    if (!pixelPos) {
      followAnimationId = requestAnimationFrame(follow)
      return
    }
    
    const [nodePixelX, nodePixelY] = pixelPos
    
    // Get chart center
    const width = chartInstance.getWidth()
    const height = chartInstance.getHeight()
    const centerX = width / 2
    const centerY = height / 2
    
    // Calculate offset needed
    const targetDx = centerX - nodePixelX
    const targetDy = centerY - nodePixelY
    
    // Apply smoothed movement using lerp
    const dx = targetDx * smoothFactor
    const dy = targetDy * smoothFactor
    
    // Apply roam if movement is significant enough
    if (Math.abs(targetDx) > 0.5 || Math.abs(targetDy) > 0.5) {
      chartInstance.dispatchAction({
        type: 'graphRoam',
        seriesIndex: 0,
        dx: dx,
        dy: dy
      })
    }
    
    // Check if node position is stable (layout stopped changing)
    if (lastNodeX === nodeX && lastNodeY === nodeY) {
      stableCount++
      // Stop when layout is stable AND we're close to center
      if (stableCount >= stableThreshold && Math.abs(targetDx) < 5 && Math.abs(targetDy) < 5) {
        stopFollowingNode()
        return
      }
    } else {
      stableCount = 0
      lastNodeX = nodeX
      lastNodeY = nodeY
    }
    
    // Continue following
    followAnimationId = requestAnimationFrame(follow)
  }
  
  // Start following
  followAnimationId = requestAnimationFrame(follow)
}

// Watch for step changes
watch(currentStep, handleStepChange)

// Schedule next step based on current step's content
const scheduleNextStep = () => {
  if (!isPlaying.value || !trajectoryData.value) return
  
  if (currentStep.value >= totalSteps.value - 1) {
    isPlaying.value = false
    return
  }
  
  const stepData = trajectoryData.value.trajectory[currentStep.value]
  const prevTarget = getPreviousStepTarget(currentStep.value)
  
  // Check if current step has target_page (and not already showing highlight from prev step)
  if (!prevTarget && stepData.target_page && stepData.navigate_domain) {
    // Wait for transition animation to complete before advancing
    onTransitionComplete = () => {
      if (isPlaying.value && currentStep.value < totalSteps.value - 1) {
        currentStep.value++
        scheduleNextStep()
      }
    }
  } else {
    // No target_page, use fixed 2 second delay
    playInterval = setTimeout(() => {
      if (isPlaying.value && currentStep.value < totalSteps.value - 1) {
        currentStep.value++
        scheduleNextStep()
      }
    }, 2000)
  }
}

// Auto-play logic
watch(isPlaying, async (playing) => {
  if (playing) {
    // Check if current step has target_page and should start transition
    if (trajectoryData.value && currentStep.value < totalSteps.value) {
      const stepData = trajectoryData.value.trajectory[currentStep.value]
      const prevTarget = getPreviousStepTarget(currentStep.value)
      
      // Only start transition if current step has target_page AND we're not already showing a highlight from prev step
      if (!prevTarget && stepData.target_page && stepData.navigate_domain) {
        const tabId = domainToTab[stepData.navigate_domain]
        if (tabId) {
          // Switch tab first if needed
          if (activeTab.value !== tabId) {
            await switchTab(tabId)
          }
          // Then start transition
          startHighlightTransition(tabId, stepData.target_page)
        }
      }
    }
    
    // Start scheduling
    scheduleNextStep()
  } else {
    if (playInterval) {
      clearTimeout(playInterval)
      playInterval = null
    }
    // Clear pending callback
    onTransitionComplete = null
    // Stop transition animation
    stopTransitionAnimation()
    // Stop following node
    stopFollowingNode()
    // Hide overlay
    showNavigatingOverlay.value = false
    
    // Set correct display state based on current step
    // If previous step had target_page, show full highlight (without following)
    // If current step has target_page (was in transition), remove partial highlight
    const prevTarget = getPreviousStepTarget(currentStep.value)
    if (prevTarget) {
      // Previous step had target_page, this step should show full red highlight
      const { tabId, targetPage } = prevTarget
      if (activeTab.value === tabId) {
        // Remove any partial highlight first
        removeHighlight()
        // Apply full highlight without following (paused state)
        applyFullHighlight(tabId, targetPage, false)
      }
    } else {
      // Current step might have been in transition, remove partial highlight
      removeHighlight()
    }
  }
})

onUnmounted(() => {
  if (playInterval) {
    clearTimeout(playInterval)
  }
  stopFollowingNode()
  stopTransitionAnimation()
})

// Load trajectory data
const loadTrajectory = async () => {
  try {
    const response = await fetch(`${TRAJECTORY_PATH}/760.json`)
    trajectoryData.value = await response.json()
  } catch (error) {
    console.error('Failed to load trajectory data:', error)
  }
}

const GRAPH_TABS = [
  { id: 'map', name: 'Map', path: '/graph/run_id-20251111-180558-map-20' },
  { id: 'admin', name: 'Admin', path: '/graph/run_id-20251026-151146-admin-124' },
  { id: 'gitlab', name: 'GitLab', path: '/graph/run_id-20251026-190417-gitlab-827' },
  { id: 'shopping', name: 'Shopping', path: '/graph/run_id-20251107-133622-shopping-570' },
  { id: 'postmill', name: 'Reddit', path: '/graph/run_id-20251207-190950-postmill-225' },
]

const activeTab = ref('map')

// Single chart instance
const chartRef = ref(null)
let chartInstance = null

// Cache for graph data and processed nodes
const graphDataMap = reactive({})
const processedNodesMap = reactive({}) // Pre-processed node data with bordered images
const isLoading = ref(true)
const currentTabLoading = ref(false)

const switchTab = async (tabId) => {
  if (activeTab.value === tabId) return
  activeTab.value = tabId
  await renderChart(tabId)
}

const createBorderedImage = (imageSrc, borderColor, borderWidth) => {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const padding = borderWidth
      const radius = 8
      canvas.width = img.width + padding * 2
      canvas.height = img.height + padding * 2
      const ctx = canvas.getContext('2d')
      
      const hexToRgba = (hex, alpha) => {
        const r = parseInt(hex.slice(1, 3), 16)
        const g = parseInt(hex.slice(3, 5), 16)
        const b = parseInt(hex.slice(5, 7), 16)
        return `rgba(${r}, ${g}, ${b}, ${alpha})`
      }
      
      ctx.fillStyle = hexToRgba(borderColor, 0.7)
      ctx.beginPath()
      ctx.roundRect(0, 0, canvas.width, canvas.height, radius + padding / 2)
      ctx.fill()
      
      ctx.save()
      ctx.beginPath()
      ctx.roundRect(padding, padding, img.width, img.height, radius)
      ctx.clip()
      ctx.drawImage(img, padding, padding, img.width, img.height)
      ctx.restore()
      
      resolve(canvas.toDataURL('image/png'))
    }
    img.onerror = () => {
      resolve(imageSrc)
    }
    img.src = imageSrc
  })
}

// Load graph data (JSON only, no image processing)
const loadGraphData = async (tabId) => {
  if (graphDataMap[tabId]) return graphDataMap[tabId]
  
  const tab = GRAPH_TABS.find(t => t.id === tabId)
  if (!tab) return null
  
  try {
    const response = await fetch(`${tab.path}/web_graph.json`)
    const data = await response.json()
    graphDataMap[tabId] = data
    return data
  } catch (error) {
    console.error(`Failed to load graph data for ${tabId}:`, error)
    return null
  }
}

// Process nodes with bordered images (heavy operation, done lazily)
const processNodes = async (tabId) => {
  if (processedNodesMap[tabId]) return processedNodesMap[tabId]
  
  const graphData = graphDataMap[tabId]
  const tab = GRAPH_TABS.find(t => t.id === tabId)
  if (!graphData || !tab) return null
  
  const graphPath = tab.path
  const nodes = []
  const nodeValues = Object.values(graphData.nodes)
  
  // Process in batches to avoid blocking
  const batchSize = 10
  for (let i = 0; i < nodeValues.length; i += batchSize) {
    const batch = nodeValues.slice(i, i + batchSize)
    const batchResults = await Promise.all(batch.map(async (node) => {
      const imagePath = `${graphPath}/screenshots_cropped_resized/${node.screen_path}`
      const isRootNode = node.screen_path.includes('start')
      
      let borderColor = '#3b82f6'
      if (!isRootNode) {
        borderColor = node.can_arrival_directly ? '#10b981' : '#f59e0b'
      }
      
      const borderWidth = isRootNode ? 4 : 3
      const borderedImage = await createBorderedImage(imagePath, borderColor, borderWidth)
      
      return {
        id: node.node_id,
        name: node.url.split('/').pop() || 'home',
        symbol: `image://${borderedImage}`,
        symbolSize: [128 + borderWidth * 2, 72 + borderWidth * 2],
        label: { show: false }
      }
    }))
    nodes.push(...batchResults)
    
    // Yield to main thread
    await new Promise(resolve => setTimeout(resolve, 0))
  }
  
  processedNodesMap[tabId] = nodes
  return nodes
}

// Render chart with specific tab data
const renderChart = async (tabId) => {
  if (!chartRef.value) return
  
  currentTabLoading.value = true
  
  // Load data if not cached
  const graphData = await loadGraphData(tabId)
  if (!graphData) {
    currentTabLoading.value = false
    return
  }
  
  // Process nodes if not cached
  const nodes = await processNodes(tabId)
  if (!nodes) {
    currentTabLoading.value = false
    return
  }
  
  // Initialize chart if needed
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.getZr().on('mousewheel', (e) => e.stop())
  }
  
  const tab = GRAPH_TABS.find(t => t.id === tabId)
  
  // Build edges
  const edgeDataMap = new Map()
  const edges = graphData.edges.map((edge, index) => {
    const edgeId = `edge_${index}`
    edgeDataMap.set(edgeId, edge)
    return {
      id: edgeId,
      source: edge.from_node_id,
      target: edge.to_node_id,
      lineStyle: { color: '#94a3b8', width: 1.5, curveness: 0 },
      symbol: ['none', 'arrow'],
      symbolSize: [4, 8]
    }
  })
  
  const option = {
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params) => {
        if (params.dataType === 'node') {
          const node = graphData.nodes[params.data.id]
          if (!node) return ''
          const displayPath = node.url.replace(/^https?:\/\/[^/]+/, '') || '/'
          return `
            <div style="max-width: 350px;">
              <strong style="display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${node.url}">${displayPath}</strong>
              <span style="color: ${node.can_arrival_directly ? '#10b981' : '#f59e0b'}">
                ${node.can_arrival_directly ? '✓ Direct Access' : '⚠ Requires Navigation'}
              </span>
            </div>
          `
        }
        if (params.dataType === 'edge') {
          const edge = edgeDataMap.get(params.data.id)
          if (edge?.action?.action_entries?.[0]) {
            const entry = edge.action.action_entries[0]
            return `
              <div>
                <span style="color: #3b82f6; font-weight: bold;">${entry.action_type || ''}</span>
                <span style="color: #8b5cf6;">[${entry.target_node_info?.role || ''}]</span>
                <span style="color: #10b981;">"${entry.target_node_info?.accessible_name || ''}"</span>
              </div>
            `
          }
        }
        return ''
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      animation: false,
      roam: true,
      roamTrigger: 'global',
      zoom: 0.5,
      scaleLimit: { min: 0.001, max: 1.5 },
      draggable: false,
      data: nodes,
      edges: edges,
      force: {
        repulsion: 2000,
        gravity: 0.05,
        edgeLength: [200, 350],
        friction: 0.6,
        layoutAnimation: true
      },
      emphasis: { disabled: true },
      lineStyle: { opacity: 0.6 }
    }]
  }
  
  chartInstance.setOption(option, true) // true = not merge, replace
  currentTabLoading.value = false
  
  // Re-apply highlight if this tab should have one
  await new Promise(resolve => setTimeout(resolve, 50))
  if (currentHighlightTarget.value && currentHighlightTarget.value.tabId === tabId) {
    applyFullHighlight(tabId, currentHighlightTarget.value.targetPage)
  }
}

// Get current graph data for display
const currentGraphData = computed(() => graphDataMap[activeTab.value])

onMounted(async () => {
  // Load trajectory data first (small)
  await loadTrajectory()
  
  // Wait for chart ref
  await new Promise(resolve => setTimeout(resolve, 50))
  
  // Load and render only the initial tab
  await renderChart(activeTab.value)
  isLoading.value = false
  
  // Pre-generate highlighted images for trajectory target pages
  await preloadHighlightedImages()
  
  // Check initial step for target_page highlight
  handleStepChange(currentStep.value)
  
  // Handle window resize
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<template>
  <section id="visualization" class="py-16 bg-gray-50">
    <div class="max-w-screen-2xl mx-auto px-4">
      <h2 class="section-title">Interactive Visualization</h2>

      <p class="text-gray-600 mb-8">
        Watch WebNavigator in action as it navigates complex web tasks using the 
        Retrieve-Reason-Teleport workflow. The right panel shows the Interaction Graph being traversed.
      </p>

      <!-- Two Column Layout (horizontal on desktop, vertical on mobile) -->
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Top/Left: Trajectory Player -->
        <div class="w-full lg:w-[60%]">
          <div class="bg-white rounded-2xl shadow-xl overflow-hidden h-full">
            <!-- Browser Chrome -->
            <div class="bg-gray-100 px-4 py-3 flex items-center gap-2 border-b">
              <div class="flex gap-1.5">
                <div class="w-3 h-3 rounded-full bg-red-400"></div>
                <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div class="w-3 h-3 rounded-full bg-green-400"></div>
              </div>
              <div class="flex-1 mx-4">
                <div class="bg-white rounded-md px-3 py-1.5 text-sm text-gray-500 border truncate">
                  {{ currentUrl || 'Loading...' }}
                </div>
              </div>
            </div>

            <!-- Visualization Content Area - 16:9 aspect ratio -->
            <div class="relative bg-gray-900 flex items-center justify-center aspect-video overflow-hidden">
              <img 
                v-if="trajectoryData"
                :src="currentScreenshot" 
                alt="Agent screenshot"
                class="w-full h-full object-contain"
              />
              <div v-else class="text-center text-white">
                <div class="text-4xl mb-4 animate-spin">⏳</div>
                <p class="text-gray-400">Loading trajectory...</p>
              </div>
              
              <!-- Navigating Overlay -->
              <Transition
                enter-active-class="transition-opacity duration-500"
                leave-active-class="transition-opacity duration-300"
                enter-from-class="opacity-0"
                leave-to-class="opacity-0"
              >
                <div 
                  v-if="showNavigatingOverlay"
                  class="absolute inset-0 bg-black/50 flex items-center justify-center"
                >
                  <div class="text-center">
                    <div class="inline-block w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin mb-4"></div>
                    <p class="text-white text-lg font-medium">Retrieving and Navigating...</p>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- Controls -->
            <div class="bg-gray-100 px-2 sm:px-4 py-3 flex items-center gap-2 sm:gap-4">
              <!-- Previous button -->
              <button 
                @click="prevStep"
                :disabled="currentStep === 0"
                class="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 flex items-center justify-center transition-colors flex-shrink-0"
              >
                ⏮
              </button>
              
              <!-- Play/Pause button -->
              <button 
                @click="togglePlay"
                class="w-10 h-10 rounded-full bg-blue-500 hover:bg-blue-600 text-white flex items-center justify-center transition-colors flex-shrink-0"
              >
                <span v-if="!isPlaying">▶</span>
                <span v-else>⏸</span>
              </button>
              
              <!-- Next button -->
              <button 
                @click="nextStep"
                :disabled="currentStep >= totalSteps - 1"
                class="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 flex items-center justify-center transition-colors flex-shrink-0"
              >
                ⏭
              </button>

              <!-- Progress Bar with Step Nodes -->
              <div 
                class="flex-1 h-2 bg-gray-300 rounded-full cursor-pointer relative min-w-0"
                @click="(e) => { const rect = e.currentTarget.getBoundingClientRect(); const percent = (e.clientX - rect.left) / rect.width; goToStep(Math.round(percent * (totalSteps - 1))); }"
              >
                <!-- Progress Fill -->
                <div 
                  class="h-full bg-blue-500 transition-all duration-300 pointer-events-none rounded-full"
                  :style="{ width: totalSteps > 1 ? `${(currentStep / (totalSteps - 1)) * 100}%` : '0%' }"
                ></div>
                <!-- Step Nodes -->
                <div 
                  v-for="step in totalSteps" 
                  :key="step"
                  class="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 transition-all duration-300 cursor-pointer hover:scale-125"
                  :class="step - 1 <= currentStep ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-400'"
                  :style="{ left: totalSteps > 1 ? `calc(${((step - 1) / (totalSteps - 1)) * 100}% - 6px)` : '0' }"
                  @click.stop="goToStep(step - 1)"
                ></div>
              </div>

              <!-- Step Indicator -->
              <span class="text-xs sm:text-sm text-gray-600 min-w-[60px] sm:min-w-[80px] text-right flex-shrink-0">
                {{ currentStep + 1 }}/{{ totalSteps }}
              </span>
            </div>
          </div>
        </div>

        <!-- Bottom/Right: Interaction Graph -->
        <div class="w-full lg:w-[40%]">
          <div class="bg-white rounded-2xl shadow-xl overflow-hidden h-full">
            <!-- Tabs -->
            <div class="bg-gray-100 px-4 py-2 flex items-center gap-1 border-b overflow-x-auto">
              <button
                v-for="tab in GRAPH_TABS"
                :key="tab.id"
                @click="switchTab(tab.id)"
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors whitespace-nowrap"
                :class="activeTab === tab.id 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-600 hover:bg-gray-200'"
              >
                {{ tab.name }}
              </button>
            </div>
            
            <!-- Header -->
            <div class="bg-gray-50 px-4 py-2 flex items-center justify-between border-b">
              <span class="text-sm font-medium text-gray-700">Interaction Graph</span>
              <span class="text-xs text-gray-500" v-if="currentGraphData">
                {{ currentGraphData.summary.total_nodes }} nodes
              </span>
            </div>

            <!-- Single chart container -->
            <div class="relative h-[300px] sm:h-[350px] lg:h-[450px]">
              <div ref="chartRef" class="w-full h-full"></div>
              
              <!-- Loading overlay -->
              <div 
                v-if="isLoading || currentTabLoading" 
                class="absolute inset-0 flex items-center justify-center bg-gray-50/80 z-10"
              >
                <div class="text-gray-500 text-sm">Loading...</div>
              </div>
            </div>

            <!-- Legend -->
            <div class="bg-gray-50 px-4 py-2 border-t flex flex-col gap-1 text-xs">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 border-2 border-blue-500 rounded"></div>
                <span class="text-gray-600">Root Node (Start)</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 border-2 border-green-500 rounded"></div>
                <span class="text-gray-600">Direct Access</span>
              </div>
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 border-2 border-amber-500 rounded"></div>
                <span class="text-gray-600">Requires Navigation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
