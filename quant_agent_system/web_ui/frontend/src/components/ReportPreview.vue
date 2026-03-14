<template>
  <div class="report-wrapper">
    <div class="header-bar">
      <h3>📄 终局研报预览</h3>
      <el-button type="success" size="small" :disabled="!markdown" @click="downloadHtml">
        下载报告
      </el-button>
    </div>
    
    <div v-if="isLoading" class="skeleton-area">
      <el-skeleton :rows="10" animated />
    </div>
    
    <el-empty v-else-if="!markdown" description="报告生成中..."></el-empty>
    
    <div v-else class="markdown-body" v-html="compiledMarkdown"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  markdown: String,
  isLoading: Boolean
})

const compiledMarkdown = computed(() => {
  if (!props.markdown) return ''
  // 渲染并防止 XSS 注入
  const rawHtml = marked.parse(props.markdown)
  return DOMPurify.sanitize(rawHtml)
})

const downloadHtml = () => {
  const blob = new Blob([compiledMarkdown.value], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'Quant_Report.html'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.report-wrapper { padding: 20px; height: 100%; display: flex; flex-direction: column; }
.header-bar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ebeef5; padding-bottom: 10px; margin-bottom: 20px; }
.skeleton-area { padding: 20px; }
.markdown-body { flex: 1; overflow-y: auto; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }
.markdown-body :deep(h2) { border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
.markdown-body :deep(table) { border-collapse: collapse; width: 100%; margin-bottom: 15px; }
.markdown-body :deep(th), .markdown-body :deep(td) { border: 1px solid #dfe2e5; padding: 6px 13px; }
.markdown-body :deep(th) { background-color: #f6f8fa; }
</style>
