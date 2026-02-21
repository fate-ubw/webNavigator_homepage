<script setup>
import tableData from '../data/table1.json'
import ablationData from '../data/table2.json'

const getCellClass = (row, key) => {
  const classes = []
  
  if (row.isOurs) {
    classes.push('bg-blue-50')
  }
  if (row.isEnterprise) {
    classes.push('bg-gray-100')
  }
  
  if (row.highlights && row.highlights[key]) {
    if (row.highlights[key] === 'best') {
      classes.push('font-bold text-blue-700')
    } else if (row.highlights[key] === 'second') {
      classes.push('underline')
    }
  }
  
  return classes.join(' ')
}

const getAlignClass = (align) => {
  if (align === 'center') return 'text-center'
  if (align === 'right') return 'text-right'
  return 'text-left'
}
</script>

<template>
  <section id="results" class="py-16 bg-white">
    <div class="max-w-6xl mx-auto px-4">
      <h2 class="section-title">Results</h2>

      <p class="text-gray-600 mb-6">
        Main results on WebArena and Online-Mind2Web. Model denotes the base LLM or VLM for action generation. Act # indicates the number of actions. Success rate (SR) for different website domains. <strong>Bold</strong> and <span class="underline">underlined</span> values indicate the best and second-best performance among non-enterprise agents. Methods marked with * are reproduced results. Models marked with † are finetuned.
      </p>

      <!-- Main Results Table -->
      <div class="overflow-x-auto mb-10">
        <table class="w-full text-sm border-collapse">
          <!-- Header -->
          <thead>
            <!-- Group Header -->
            <tr class="border-b-2 border-gray-300">
              <th class="py-2 px-2" colspan="3"></th>
              <th class="py-2 px-2 bg-orange-50 text-orange-800 font-semibold" colspan="7">WebArena</th>
              <th class="py-2 px-2 bg-blue-50 text-blue-800 font-semibold" colspan="1">Online-Mind2Web</th>
            </tr>
            <!-- Column Header -->
            <tr class="border-b border-gray-200 bg-gray-50">
              <th 
                v-for="col in tableData.columns" 
                :key="col.key"
                class="py-2 px-2 font-semibold text-gray-700"
                :class="[
                  getAlignClass(col.align),
                  col.group === 'webarena' ? 'bg-orange-50/50' : '',
                  col.group === 'mind2web' ? 'bg-blue-50/50' : ''
                ]"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          
          <!-- Body -->
          <tbody>
            <template v-for="(section, sIdx) in tableData.sections" :key="sIdx">
              <!-- Section Header -->
              <tr class="bg-gray-100">
                <td colspan="11" class="py-2 px-2 text-center text-gray-600 italic text-sm">
                  {{ section.title }}
                </td>
              </tr>
              
              <!-- Data Rows -->
              <tr 
                v-for="(row, rIdx) in section.rows" 
                :key="`${sIdx}-${rIdx}`"
                class="border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
                :class="{ 'bg-blue-50/70': row.isOurs, 'bg-gray-50': row.isEnterprise }"
              >
                <td 
                  v-for="col in tableData.columns" 
                  :key="col.key"
                  class="py-2 px-2"
                  :class="[
                    getAlignClass(col.align),
                    getCellClass(row, col.key),
                    col.group === 'webarena' ? 'bg-orange-50/30' : '',
                    col.group === 'mind2web' ? 'bg-blue-50/30' : '',
                    row.isOurs && col.key === 'method' ? 'text-blue-700 font-medium' : ''
                  ]"
                >
                  {{ row[col.key] }}
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Performance Summary Cards -->
      <div class="grid md:grid-cols-2 gap-8 mt-10">
        <!-- <div class="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl">
          <h3 class="font-semibold text-lg text-gray-900 mb-4">WebArena Highlights</h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Best Overall SR</span>
              <span class="font-bold text-green-600">60.2%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Best Multi-site SR</span>
              <span class="font-bold text-green-600">72.9%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Best Reddit SR</span>
              <span class="font-bold text-green-600">85.9%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">vs Enterprise (CUGA)</span>
              <span class="font-bold text-green-600">2× on Multi-site</span>
            </div>
          </div>
        </div> -->

        <!-- <div class="bg-gradient-to-br from-purple-50 to-indigo-50 p-6 rounded-xl">
          <h3 class="font-semibold text-lg text-gray-900 mb-4">Online-Mind2Web Highlights</h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Best Success Rate</span>
              <span class="font-bold text-purple-600">52.7%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Average Actions</span>
              <span class="font-bold text-purple-600">6</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">vs WebDreamer</span>
              <span class="font-bold text-purple-600">+17.7%</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">vs Agent-E</span>
              <span class="font-bold text-purple-600">+25.7%</span>
            </div>
          </div>
        </div> -->
      </div>

      <!-- Ablation Studies -->
      <div class="mt-10">
        <h3 class="font-semibold text-lg text-gray-900 mb-4">Ablation Studies</h3>
        <p class="text-gray-600 mb-4">
          {{ ablationData.caption }}
        </p>
        
        <div class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <!-- Header -->
            <thead>
              <tr class="border-b-2 border-gray-300 bg-gray-50">
                <th 
                  v-for="col in ablationData.columns" 
                  :key="col.key"
                  class="py-2 px-3 font-semibold text-gray-700"
                  :class="getAlignClass(col.align)"
                >
                  {{ col.label }}
                </th>
              </tr>
            </thead>
            
            <!-- Body -->
            <tbody>
              <template v-for="(section, sIdx) in ablationData.sections" :key="sIdx">
                <!-- Section Header -->
                <tr class="bg-gray-100">
                  <td colspan="6" class="py-2 px-3 text-center text-gray-600 italic text-sm">
                    {{ section.title }}
                  </td>
                </tr>
                
                <!-- Data Rows -->
                <tr 
                  v-for="(row, rIdx) in section.rows" 
                  :key="`abl-${sIdx}-${rIdx}`"
                  class="border-b border-gray-100 hover:bg-gray-50/50 transition-colors"
                  :class="{ 'bg-green-50/50': row.isBest }"
                >
                  <td 
                    v-for="col in ablationData.columns" 
                    :key="col.key"
                    class="py-2 px-3"
                    :class="[
                      getAlignClass(col.align),
                      row.isBest && col.key === 'sr' ? 'font-bold text-green-700' : ''
                    ]"
                  >
                    {{ row[col.key] }}
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>
