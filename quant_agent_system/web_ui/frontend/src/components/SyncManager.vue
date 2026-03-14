<template>
  <div class="sync-manager">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>🔄 数据库同步管理</span>
        </div>
      </template>

      <!-- 同步状态 -->
      <div class="status-section">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-statistic title="关注股票数" :value="syncStatus.watched_stocks_count" />
          </el-col>
          <el-col :span="12">
            <el-statistic title="调度器状态">
              <template #default>
                <el-tag :type="syncStatus.scheduler_running ? 'success' : 'info'">
                  {{ syncStatus.scheduler_running ? '运行中' : '已停止' }}
                </el-tag>
              </template>
            </el-statistic>
          </el-col>
        </el-row>

        <el-divider />

        <!-- 最后同步信息 -->
        <div v-if="syncStatus.last_sync" class="last-sync-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(syncStatus.last_sync.status)">
                {{ syncStatus.last_sync.status || '无' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="更新股票数">
              {{ syncStatus.last_sync.stocks_updated || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatTime(syncStatus.last_sync.start_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ formatTime(syncStatus.last_sync.end_time) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <el-empty v-else description="暂无同步记录" :image-size="60" />

        <el-divider />

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button type="primary" @click="triggerSync" :loading="syncing">
            立即同步
          </el-button>
          <el-button @click="fetchStatus">刷新状态</el-button>
        </div>
      </div>

      <!-- 同步日志 -->
      <el-divider content-position="left">同步日志</el-divider>
      <el-table :data="logs" size="small" max-height="200">
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stocks_updated" label="股票数" width="80" />
        <el-table-column prop="start_time" label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="error" label="错误信息">
          <template #default="{ row }">
            <span v-if="row.error" style="color: red;">{{ row.error }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const syncStatus = ref({
  watched_stocks_count: 0,
  scheduler_running: false,
  last_sync: null
})
const logs = ref([])
const syncing = ref(false)

const fetchStatus = async () => {
  try {
    const res = await axios.get('/api/sync/status')
    if (res.data.success) {
      syncStatus.value = res.data.data
    }
  } catch (e) {
    console.error('获取状态失败', e)
  }
}

const fetchLogs = async () => {
  try {
    const res = await axios.get('/api/sync/logs?limit=20')
    if (res.data.success) {
      logs.value = res.data.data
    }
  } catch (e) {
    console.error('获取日志失败', e)
  }
}

const triggerSync = async () => {
  syncing.value = true
  try {
    const res = await axios.post('/api/sync/trigger')
    if (res.data.success) {
      ElMessage.success('同步已触发')
      setTimeout(() => {
        fetchStatus()
        fetchLogs()
      }, 1000)
    } else {
      ElMessage.error(res.data.error || '同步失败')
    }
  } catch (e) {
    ElMessage.error('同步请求失败')
  } finally {
    syncing.value = false
  }
}

const getStatusType = (status) => {
  if (status === 'success') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'failed') return 'danger'
  return 'info'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    return new Date(timeStr).toLocaleString('zh-CN')
  } catch {
    return timeStr
  }
}

onMounted(() => {
  fetchStatus()
  fetchLogs()
})
</script>

<style scoped>
.sync-manager {
  margin-bottom: 15px;
}
.card-header {
  font-weight: 600;
}
.status-section {
  padding: 10px 0;
}
.last-sync-info {
  margin: 10px 0;
}
.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}
</style>
