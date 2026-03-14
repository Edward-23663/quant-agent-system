<template>
  <el-card shadow="hover" class="chart-card">
    <template #header>
      <div class="card-header">
        <span>📊 物理图表挂载区</span>
      </div>
    </template>
    <el-empty v-if="chartUrls.length === 0" description="暂无图表生成" :image-size="60"></el-empty>
    <div v-else class="image-list">
      <el-image 
        v-for="(url, index) in chartUrls" 
        :key="index" 
        :src="url" 
        :preview-src-list="chartUrls"
        fit="contain"
        class="chart-img"
      />
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  chartUrls: Array
})
</script>

<style scoped>
.chart-card { margin-top: 20px; }
.image-list { display: flex; flex-direction: column; gap: 10px; }
.chart-img { width: 100%; border-radius: 4px; border: 1px solid #ebeef5; cursor: pointer; }
</style>
