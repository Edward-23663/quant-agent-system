<template>
  <div class="app-container">
    <el-container>
      <el-header class="header">
        <h2>🧠 金融量化分析智能体系统 (Agentic Workflow)</h2>
      </el-header>
      
      <el-container class="main-body">
        <!-- 左侧控制台 -->
        <el-aside width="350px" class="sidebar">
          <SyncManager />
          <WatchedStocks />
          <ChartViewer :chartUrls="chartUrls" />
        </el-aside>

        <!-- 中间时间轴 + 底部输入框 -->
        <el-main class="content-area">
          <div class="timeline-wrapper">
            <AgentTimeline :events="agentEvents" :isRunning="isRunning" />
          </div>
          
          <!-- 底部指令输入框 -->
          <div class="input-area">
            <el-input
              v-model="prompt"
              type="textarea"
              :rows="3"
              placeholder="例如：请帮我深度估值一下茅台(600519.SH)，看看现在能不能买？"
              @keydown.enter.ctrl="startTask"
            />
            <el-button 
              type="primary" 
              class="submit-btn" 
              @click="startTask" 
              :loading="isRunning"
            >
              🚀 启动智能体编排
            </el-button>
          </div>
        </el-main>

        <!-- 右侧：最终研报预览区 -->
        <el-aside width="500px" class="report-area">
          <ReportPreview :markdown="finalMarkdown" :isLoading="isRunning" />
        </el-aside>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import AgentTimeline from './components/AgentTimeline.vue'
import ReportPreview from './components/ReportPreview.vue'
import ChartViewer from './components/ChartViewer.vue'
import SyncManager from './components/SyncManager.vue'
import WatchedStocks from './components/WatchedStocks.vue'

const prompt = ref('请分析贵州茅台(600519.SH)的基本面健康度，并使用DCF模型测算绝对估值。')
const isRunning = ref(false)
const agentEvents = ref([])
const finalMarkdown = ref('')
const chartUrls = ref([])
let eventSource = null

const startTask = async () => {
  if (!prompt.value) return ElMessage.warning('请输入指令')
  
  isRunning.value = true
  agentEvents.value = []
  finalMarkdown.value = ''
  chartUrls.value = []

  try {
    // 1. 发送 HTTP 请求创建任务
    const res = await axios.post('/api/task', { prompt: prompt.value })
    const taskId = res.data.task_id
    
    // 2. 建立 SSE 连接监听 Redis 状态
    connectSSE(taskId)
  } catch (error) {
    ElMessage.error('任务创建失败')
    isRunning.value = false
  }
}

const connectSSE = (taskId) => {
  if (eventSource) eventSource.close()
  
  eventSource = new EventSource(`/api/stream/task/${taskId}`)
  
  // 监听普通状态消息
  eventSource.addEventListener('message', (e) => {
    const data = JSON.parse(e.data)
    agentEvents.value.push({
      timestamp: new Date().toLocaleTimeString(),
      content: data.msg,
      type: getEventType(data.msg)
    })
    
    // 拦截图表生成标记 (模拟)
    if(data.msg.includes('.png')) {
       // 提取路径逻辑，此处略，可传入 chartUrls
    }
  })

  // 监听最终报告生成
  eventSource.addEventListener('final_report', (e) => {
    const data = JSON.parse(e.data)
    finalMarkdown.value = data.markdown
    isRunning.value = false
    ElMessage.success('🎉 研报生成完毕！')
    eventSource.close()
  })

  eventSource.onerror = () => {
    eventSource.close()
    if(isRunning.value) {
        isRunning.value = false
        ElMessage.error('流式连接异常断开')
    }
  }
}

// 根据日志内容分配颜色标签
const getEventType = (msg) => {
  if (msg.includes('挂起') || msg.includes('拦截') || msg.includes('缺失')) return 'warning'
  if (msg.includes('致命') || msg.includes('失败')) return 'danger'
  if (msg.includes('成功') || msg.includes('就绪') || msg.includes('完毕')) return 'success'
  if (msg.includes('主编排器')) return 'primary'
  return 'info'
}
</script>

<style scoped>
.app-container { height: 100vh; background-color: #f0f2f5; }
.header { background-color: #1d2b36; color: white; display: flex; align-items: center; }
.main-body { height: calc(100vh - 60px); padding: 20px; gap: 20px; }
.content-area { display: flex; flex-direction: column; padding: 0 !important; background: transparent !important; }
.timeline-wrapper { flex: 1; background: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1); padding: 20px; overflow-y: auto; margin-bottom: 20px; }
.input-area { background: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1); padding: 20px; display: flex; gap: 15px; align-items: flex-start; }
.input-area .el-textarea { flex: 1; }
.submit-btn { height: fit-content; }
.report-area { background: white; border-radius: 8px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1); overflow-y: auto; }
.sidebar { display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
</style>
