<template>
  <div class="timeline-wrapper">
    <h3>⏱️ 智能体思考与执行流</h3>
    <el-empty v-if="events.length === 0" description="等待指令输入..."></el-empty>
    
    <el-timeline v-else>
      <el-timeline-item
        v-for="(activity, index) in events"
        :key="index"
        :type="activity.type"
        :timestamp="activity.timestamp"
        placement="top"
      >
        <el-card :body-style="{ padding: '10px' }" shadow="hover">
          <span :class="['log-text', activity.type]">{{ activity.content }}</span>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    
    <div v-if="isRunning" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon> 智能体正在处理中...
    </div>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
defineProps({
  events: Array,
  isRunning: Boolean
})
</script>

<style scoped>
.timeline-wrapper { padding: 10px; }
.log-text { font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.5; }
.log-text.warning { color: #e6a23c; font-weight: bold; }
.log-text.danger { color: #f56c6c; font-weight: bold; }
.log-text.success { color: #67c23a; }
.log-text.primary { color: #409eff; font-weight: bold; }
.loading-state { text-align: center; margin-top: 20px; color: #909399; }
</style>
