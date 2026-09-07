const statusCard = document.querySelector('#status-card');
const stepLabel = document.querySelector('#step-label');
const statusTag = document.querySelector('#status-tag');
const statusTitle = document.querySelector('#status-title');
const statusCopy = document.querySelector('#status-copy');
const serviceIndicator = document.querySelector('#service-indicator');
const sourceTitle = document.querySelector('#source-title');
const sourceMeta = document.querySelector('#source-meta');
const qualityCard = document.querySelector('#quality-card');
const staticImageQualitySelect = document.querySelector('#static-image-quality');
const titleImageBrandSelect = document.querySelector('#title-image-brand');
const packageCard = document.querySelector('#package-card');
const metricBlocks = document.querySelector('#metric-blocks');
const metricImages = document.querySelector('#metric-images');
const metricState = document.querySelector('#metric-state');
const compileProgress = document.querySelector('#compile-progress');
const progressPhase = document.querySelector('#progress-phase');
const progressPercent = document.querySelector('#progress-percent');
const progressTrack = document.querySelector('.progress-track');
const progressBar = document.querySelector('#progress-bar');
const progressDetail = document.querySelector('#progress-detail');
const progressElapsed = document.querySelector('#progress-elapsed');
const cancelCompileButton = document.querySelector('#cancel-compile');
const pageNotice = document.querySelector('#page-notice');
const pageNoticeTitle = document.querySelector('#page-notice-title');
const pageNoticeCopy = document.querySelector('#page-notice-copy');
const injectButton = document.querySelector('#inject');
const clearSourceButton = document.querySelector('#clear-source');
const resultCard = document.querySelector('#result-card');
const resultTitle = document.querySelector('#result-title');
const resultCopy = document.querySelector('#result-copy');
const result = document.querySelector('#result');
const copyResultButton = document.querySelector('#copy-result');
const gifIssuePanel = document.querySelector('#gif-issue-panel');
const toggleGifIssuesButton = document.querySelector('#toggle-gif-issues');
const gifIssueList = document.querySelector('#gif-issue-list');
const sourceLink = globalThis.IFANR_SOURCE_LINK;
const pageState = globalThis.IFANR_PAGE_STATE;
const writeGuard = globalThis.IFANR_WECHAT_WRITE_GUARD;
const titleImageBrand = globalThis.IFANR_TITLE_IMAGE_BRAND;

const SOURCE_KEY = 'ifanrFeishuSource';
const PACKAGE_KEY = 'ifanrArticlePackage';
const STATUS_KEY = 'ifanrCompileStatus';
const LAST_RESULT_KEY = 'ifanrLastResult';
const PAGE_STATUS_KEY = 'ifanrWechatPageStatus';
const WRITE_STATUS_KEY = 'ifanrWechatWriteStatus';
const STATIC_IMAGE_QUALITY_KEY = 'ifanrStaticImageQuality';
const TITLE_IMAGE_BRAND_KEY = 'ifanrTitleImageBrand';
const ACCEPTED_STYLE_VERSIONS = new Set(['ifanr-wechat-compatible-v3', 'ifanr-wechat-compatible-v5-browser', 'ifanr-wechat-compatible-v6-browser']);
const WECHAT_IMAGE_MAX_BYTES = 5 * 1024 * 1024;

let activeTab;
let wechatEditorTabs = [];
let storedSource;
let storedPackage;
let compileStatus;
let wechatPageStatus;
let wechatWriteStatus;
let currentAction = null;
let actionRunning = false;
let progressClock = null;
let outdatedPackageDiscarded = false;
let outdatedPackageSourceUrl = null;
let writeFailurePending = false;
let staticImageQuality = 90;
let titleImageBrandPreference = 'auto';

function normalizedStaticImageQuality(value) {
  const numeric = Number(value);
  return [75, 90, 95].includes(numeric) ? numeric : 90;
}

function normalizedTitleImageBrand(value) {
  return titleImageBrand?.normalizePreference(value) || (['auto', 'ifanr', 'appso'].includes(value) ? value : 'auto');
}

function titleImageBrandLabel(articlePackage) {
  const brand = articlePackage?.titleImageBrand || articlePackage?.titleImageSelection?.brand;
  return brand === 'appso' ? 'AppSo 题图' : brand === 'ifanr' ? '爱范儿题图' : '';
}

function cleanDisplayTitle(value = '') {
  return String(value).replace(/\p{Cf}/gu, '').trim();
}

function manualImageReplacementsForPackage(articlePackage) {
  const warnings = [
    ...(articlePackage?.gifWarnings || []),
    ...(articlePackage?.mediaWarnings || []).filter((warning) => warning.code === 'wechat-size-limit')
  ];
  const byOrder = new Map();
  warnings
    .filter((image) => Number(image.bytes || 0) > WECHAT_IMAGE_MAX_BYTES)
    .forEach((image) => byOrder.set(Number(image.order), {
      order: Number(image.order),
      name: image.name || `第 ${image.order} 张图片`,
      bytes: Number(image.bytes || 0),
      reason: '超过微信 5MB 上限'
    }));
  return [...byOrder.values()].filter((image) => image.order > 0);
}

function packageOptions(articlePackage) {
  const manualImageReplacements = manualImageReplacementsForPackage(articlePackage);
  return {
    clickSaveAsDraft: true,
    timeoutMs: 45000,
    imageStallTimeoutMs: 8000,
    saveStallTimeoutMs: 3000,
    sourceImageCount: articlePackage.imageCount,
    expectedImageCount: Math.max(0, articlePackage.imageCount - manualImageReplacements.length),
    manualImageReplacements,
    requireHostedImages: articlePackage.imageCount - manualImageReplacements.length > 0,
    expectedTextContains: articlePackage.expectedTextContains,
    articleTitle: articlePackage.title || '',
    articleSummary: articlePackage.summary || '',
    forceEditorReplace: true,
    forbiddenTextMarkers: ['章节标题 v0.2', '图片链路测试 v0.3.1', '图片托管确认 v0.4']
  };
}

function setStatus({ step, tag, title, copy, tone = 'neutral' }) {
  stepLabel.textContent = step;
  statusTag.textContent = tag;
  statusTitle.textContent = title;
  statusCopy.textContent = copy;
  statusCard.dataset.tone = tone;
  statusCard.setAttribute('aria-live', tone === 'danger' ? 'assertive' : 'polite');
}

function setPrimary(label, action, enabled = true) {
  injectButton.textContent = label;
  injectButton.disabled = !enabled || actionRunning;
  currentAction = enabled ? action : null;
}

async function queryWechatEditorTabs() {
  let tabs = [];
  try {
    tabs = await chrome.tabs.query({ url: 'https://mp.weixin.qq.com/*' });
  } catch {
    tabs = [];
  }
  return writeGuard.findEditorTabs(tabs, activeTab, sourceLink);
}

async function failStaleWechatWrite(reason) {
  if (!reason || wechatWriteStatus?.state !== 'processing' || writeFailurePending) return;
  writeFailurePending = true;
  const completedAt = new Date().toISOString();
  const failed = {
    ...wechatWriteStatus,
    state: 'failed',
    phase: 'write-failed',
    completedAt,
    progress: {
      phase: 'write-failed',
      percent: Number(wechatWriteStatus.progress?.percent || 0),
      message: reason.message
    },
    error: reason
  };
  wechatWriteStatus = failed;
  try {
    await chrome.storage.local.set({ [WRITE_STATUS_KEY]: failed });
  } finally {
    writeFailurePending = false;
  }
}

function showResult({ title, copy, tone = 'neutral', detail }) {
  resultCard.hidden = false;
  resultCard.dataset.tone = tone;
  resultCard.setAttribute('aria-live', tone === 'danger' ? 'assertive' : 'polite');
  resultTitle.textContent = title;
  resultCopy.textContent = copy;
  result.textContent = typeof detail === 'string' ? detail : JSON.stringify(detail || {}, null, 2);
  setGifIssueList(extractGifIssues(detail));
}

function hideResult() {
  resultCard.hidden = true;
  result.textContent = '等待操作';
  setGifIssueList([]);
}

function extractGifIssues(detail) {
  if (!detail || typeof detail === 'string') return [];
  if (Array.isArray(detail?.error?.images)) return detail.error.images;
  if (Array.isArray(detail?.mediaWarnings)) return detail.mediaWarnings;
  if (Array.isArray(detail?.gifWarnings)) return detail.gifWarnings;
  if (Array.isArray(detail?.result?.mediaWarnings)) return detail.result.mediaWarnings;
  if (Array.isArray(detail?.result?.gifWarnings)) return detail.result.gifWarnings;
  return [];
}

function formatGifBytes(bytes) {
  const value = Number(bytes || 0);
  return value > 0 ? `${(value / 1024 / 1024).toFixed(2)}MB` : '';
}

function gifReasonLabels(issue) {
  const labels = {
    'frame-density': '帧数或帧率过高',
    'canvas-size': '画布尺寸偏大',
    'file-size': '文件体积偏大',
    'output-size': '高质量压缩后仍然偏大',
    'download-failed': '图片暂时无法读取'
  };
  const reasons = (Array.isArray(issue?.reasons) ? issue.reasons : [])
    .map((reason) => labels[reason] || reason);
  if (Number(issue?.bytes || 0) > WECHAT_IMAGE_MAX_BYTES) reasons.push('超过微信 5MB 上限');
  return [...new Set(reasons)];
}

function fallbackGifAdvice(issue) {
  const advice = [];
  const reasons = new Set(issue?.reasons || []);
  if (reasons.has('frame-density')) advice.push('优先删除重复帧，把帧数降到 100 帧以内或帧率降到 12.5fps 以内。');
  if (reasons.has('canvas-size')) advice.push('把画布长边等比缩到 960px 以内，不要裁掉关键信息。');
  if (Number(issue?.bytes || 0) > WECHAT_IMAGE_MAX_BYTES) advice.push('文件必须压到 5MB 以内，建议留出余量控制在 3.5MB 左右。');
  return advice.length ? advice : ['手动压缩或替换后重新收录，并检查动画清晰度和播放速度。'];
}

function setGifIssueList(issues = []) {
  const normalized = Array.isArray(issues) ? issues.filter(Boolean) : [];
  gifIssueList.replaceChildren();
  gifIssuePanel.hidden = normalized.length === 0;
  gifIssueList.hidden = true;
  toggleGifIssuesButton.setAttribute('aria-expanded', 'false');
  toggleGifIssuesButton.textContent = normalized.length ? `展开 ${normalized.length} 张问题图片` : '查看问题图片';
  normalized.forEach((issue, index) => {
    const item = document.createElement('article');
    item.className = 'gif-issue-item';

    const heading = document.createElement('strong');
    const order = Number(issue.order || 0);
    heading.textContent = `${order ? `第 ${order} 张` : `问题图片 ${index + 1}`}${issue.name ? ` · ${issue.name}` : ''}`;
    item.append(heading);

    const metaParts = [
      formatGifBytes(issue.bytes),
      issue.frameCount ? `${issue.frameCount} 帧` : '',
      issue.durationSeconds ? `${issue.durationSeconds} 秒` : '',
      issue.width && issue.height ? `${issue.width}×${issue.height}px` : ''
    ].filter(Boolean);
    if (metaParts.length) {
      const meta = document.createElement('div');
      meta.className = 'gif-issue-meta';
      meta.textContent = metaParts.join(' · ');
      item.append(meta);
    }

    const reasons = gifReasonLabels(issue);
    if (reasons.length) {
      const reason = document.createElement('div');
      reason.className = 'gif-issue-reason';
      reason.textContent = `问题：${reasons.join('、')}`;
      item.append(reason);
    }

    const recommendations = Array.isArray(issue.recommendations) && issue.recommendations.length
      ? issue.recommendations
      : fallbackGifAdvice(issue);
    const advice = document.createElement('ul');
    advice.className = 'gif-issue-advice';
    recommendations.forEach((recommendation) => {
      const row = document.createElement('li');
      row.textContent = recommendation;
      advice.append(row);
    });
    item.append(advice);
    gifIssueList.append(item);
  });
}

function showSource(source) {
  if (!source) {
    sourceTitle.textContent = '尚未选择飞书文档';
    sourceMeta.textContent = '请先在飞书 Wiki 或文档页面完成收录。';
    clearSourceButton.hidden = true;
    return;
  }
  sourceTitle.textContent = source.title || source.token;
  sourceMeta.textContent = source.canonicalUrl;
  clearSourceButton.hidden = false;
}

function showPackage(articlePackage, label = '已就绪') {
  packageCard.hidden = !articlePackage;
  if (!articlePackage) return;
  metricBlocks.textContent = String(articlePackage.blockCount ?? '—');
  const galleryCopy = articlePackage.galleryCount > 0 ? ` · 横滑 ${articlePackage.galleryCount} 组` : '';
  const compressedCopy = articlePackage.compressedStaticImageCount > 0 ? ` · 优化 ${articlePackage.compressedStaticImageCount} 张` : '';
  metricImages.textContent = `${articlePackage.imageCount ?? 0} 张${galleryCopy}${compressedCopy}`;
  const titleBrandCopy = titleImageBrandLabel(articlePackage);
  metricState.textContent = `${label}${titleBrandCopy ? ` · ${titleBrandCopy}` : ''}`;
}

function phaseLabel(phase) {
  return ({
    accepted: '正在连接读取服务',
    'browser-starting': '正在连接当前飞书页面',
    'browser-reading': '正在核对飞书全文',
    'browser-images': '正在读取飞书图片',
    'compressing-static-images': '正在高质量压缩超限静态图',
    'browser-rendering': '正在生成微信兼容排版',
    'service-fallback': '正在切换增强服务',
    queued: '等待开始处理',
    starting: '正在启动读取',
    'reading-document': '正在读取飞书文档',
    'parsing-document': '正在解析正文',
    'downloading-images': '正在下载图片',
    'processing-images': '正在整理图片',
    'compressing-gif': '正在压缩动图',
    'checking-gif-quality': '正在检查动图画质',
    rendering: '正在生成排版',
    packaging: '正在保存内容包',
    completed: '排版内容已准备完成',
    'preparing-write': '正在确认公众号编辑器',
    'clearing-editor': '正在备份并净空原草稿',
    'inserting-content': '正在写入正文',
    'uploading-images': '正在托管图片',
    'uploading-animated-images': '正在逐张托管动图',
    'waiting-save': '正在等待微信保存',
    'validating-write': '正在检查写入结果',
    'write-completed': '公众号排版已完成',
    'write-failed': '公众号写入未完成'
  })[phase] || '正在生成排版内容';
}

function hideCompileProgress() {
  compileProgress.hidden = true;
  if (progressClock) clearInterval(progressClock);
  progressClock = null;
}

function updateProgressClock(status) {
  const started = Date.parse(status?.startedAt || 0);
  const deadline = Date.parse(status?.deadlineAt || 0);
  const elapsed = Number.isFinite(started) ? Math.max(0, Math.floor((Date.now() - started) / 1000)) : 0;
  const total = Number.isFinite(started) && Number.isFinite(deadline)
    ? Math.max(1, Math.round((deadline - started) / 1000))
    : 45;
  progressElapsed.textContent = `${Math.min(elapsed, total)} 秒 / ${total} 秒`;
}

function showCompileProgress(status) {
  const progress = status?.progress || {};
  const percent = Math.max(0, Math.min(100, Math.round(Number(progress.percent) || 0)));
  compileProgress.hidden = false;
  progressPhase.textContent = phaseLabel(progress.phase || status?.phase);
  progressPercent.textContent = `${percent}%`;
  progressBar.style.width = `${percent}%`;
  progressTrack.setAttribute('aria-valuenow', String(percent));
  progressDetail.textContent = progress.message || '正在生成排版内容';
  const canCancel = status?.state === 'processing' && !String(progress.phase || status?.phase || '').includes('write') && ![
    'preparing-write', 'clearing-editor', 'inserting-content', 'uploading-images', 'uploading-animated-images', 'waiting-save', 'validating-write'
  ].includes(progress.phase || status?.phase);
  cancelCompileButton.hidden = !canCancel;
  cancelCompileButton.disabled = !canCancel;
  updateProgressClock(status);
  if (!progressClock) {
    progressClock = setInterval(() => {
      const activeProgress = wechatWriteStatus?.state === 'processing' ? wechatWriteStatus : compileStatus;
      if (activeProgress?.state === 'processing') {
        updateProgressClock(activeProgress);
        if (activeProgress === wechatWriteStatus) {
          const staleReason = writeGuard.staleWriteReason(wechatWriteStatus, wechatPageStatus);
          if (staleReason) void failStaleWechatWrite(staleReason);
        }
      }
    }, 1000);
  }
}

function showPageNotice(status) {
  const description = pageState.describeWechatPageStatus(status);
  pageNotice.hidden = !description;
  if (!description) return;
  pageNotice.dataset.tone = description.tone;
  pageNoticeTitle.textContent = description.title;
  pageNoticeCopy.textContent = description.message;
}

function matchesSource(value, source) {
  return Boolean(value?.sourceUrl && source && sourceLink.sameFeishuDoc(value.sourceUrl, source.canonicalUrl));
}

function readableCompileError(status) {
  const error = status?.error || {};
  const messages = {
    DYNAMIC_SERVICE_UNAVAILABLE: '本机读取服务尚未连接，请启动服务后重试。',
    SERVICE_VERSION_MISMATCH: '插件和本机服务版本不兼容，请更新后重试。',
    BOT_SCOPE_MISSING: '飞书应用缺少文档只读权限，请联系管理员开通。',
    USER_KEYCHAIN_UNAVAILABLE: '读取服务无法使用当前飞书身份，请改用已授权的只读应用。',
    IMAGE_DOWNLOAD_FAILED: '部分飞书图片下载失败，请检查网络后重试。',
    GIF_OPTIMIZER_UNAVAILABLE: 'GIF 压缩器未安装，请先安装本机图片处理组件。',
    GIF_MANUAL_OPTIMIZATION_REQUIRED: '检测到问题动图；新版会直接生成可排版版本，并把问题位置作为提醒保留。请重新收录一次。',
    GIF_TOO_LARGE_AFTER_COMPRESSION: '有一张动图压缩后仍超过 5MB，请缩短动画或降低原图尺寸。',
    IMAGE_TOO_LARGE_AFTER_COMPRESSION: '有一张图片压缩后仍超过 5MB，已停止生成以避免微信上传失败。',
    IMAGE_PROCESSING_TIMEOUT: '有一张图片处理超时，任务已经停止，可以调整图片后重试。',
    COMPILE_CANCELLED: '任务已经停止，没有写入或覆盖任何公众号内容。',
    SOURCE_MISMATCH: '返回内容与当前飞书文档不一致，已停止收录。',
    CONTENT_FIDELITY_NOT_CONFIRMED: '源文档与排版结果没有完整对应，插件已停止收录，避免缺字或掉图。请刷新飞书文档后重试。',
    FEISHU_TAB_NOT_FOUND: '没有找到仍然打开的飞书文档，请回到文档页面重新收录。',
    FEISHU_PAGE_READER_UNAVAILABLE: '飞书页面读取器尚未加载，请刷新飞书页面后重试。',
    FEISHU_DOCUMENT_NOT_READY: '飞书正文还没有加载完成，请稍等片刻后重试。',
    FEISHU_DOCUMENT_EMPTY: '当前页面没有读取到正文，请确认文档权限和加载状态。',
    FEISHU_DOCUMENT_UNSTABLE: '飞书正文仍在加载或变化，插件已停止生成，避免出现缺段。请等待页面稳定后重试。',
    FEISHU_IMAGE_DOWNLOAD_FAILED: '有图片无法通过当前飞书登录状态读取，请重新加载文档后重试。',
    FEISHU_IMAGE_DOWNLOAD_TIMEOUT: '有图片读取超过 20 秒，插件已停止等待。刷新飞书文档后可以重试。',
    FEISHU_IMAGE_FORMAT_UNSUPPORTED: '文档里有暂不支持的媒体格式，请使用本机增强服务处理。',
    FEISHU_IMAGE_TOO_LARGE: '有单张图片超过 40MB，插件已停止收录，避免浏览器卡死。',
    FEISHU_ARTICLE_MEDIA_TOO_LARGE: '文档图片总量超过 96MB，请拆分文章或使用本机增强服务。',
    FEISHU_STATIC_IMAGE_OPTIMIZATION_REQUIRED: '有静态图片超过微信 5MB 上限，请使用增强服务压缩或手动替换。',
    FEISHU_ANIMATION_UNVERIFIED: '飞书只返回了动图静态封面，插件已停止生成，避免悄悄丢失动画。'
  };
  if (error.code === 'COMPILE_TIMEOUT') {
    const image = error.imageIndex ? `第 ${error.imageIndex}${error.imageCount ? ` / ${error.imageCount}` : ''} 张图片` : '';
    const stage = error.progressMessage || phaseLabel(error.phase);
    return `处理超过 45 秒，已经自动停止。最后停在${image ? `${image}，` : '：'}${stage}。`;
  }
  if (error.code === 'GIF_MANUAL_OPTIMIZATION_REQUIRED') {
    const images = Array.isArray(error.images) ? error.images : [];
    const lines = images.filter((image) => image.order).map((image) => {
      const details = [
        image.frameCount ? `${image.frameCount} 帧` : '',
        image.durationSeconds ? `${image.durationSeconds} 秒` : '',
        image.width && image.height ? `${image.width}×${image.height}px` : '',
        image.bytes ? `${(image.bytes / 1024 / 1024).toFixed(2)}MB` : ''
      ].filter(Boolean).join(' / ');
      const advice = Array.isArray(image.recommendations) && image.recommendations.length
        ? image.recommendations.join(' ')
        : '建议把帧数降到 100 帧以内、帧率降到 12.5fps 以内、长边降到 960px 以内，并尽量压到 3.5MB 左右。';
      return `第 ${image.order} 张${image.name ? `（${image.name}）` : ''}${details ? `：${details}` : ''}\n修改建议：${advice}`;
    });
    return `${messages[error.code]}${lines.length ? `\n\n${lines.join('\n\n')}` : ''}`;
  }
  return messages[error.code] || error.message || '飞书文档读取失败，请稍后重试。';
}

function compileErrorSummary(status) {
  const error = status?.error || {};
  if (error.code !== 'GIF_MANUAL_OPTIMIZATION_REQUIRED') return readableCompileError(status);
  const images = Array.isArray(error.images) ? error.images : [];
  const overLimitCount = images.filter((image) => Number(image.bytes || 0) > WECHAT_IMAGE_MAX_BYTES).length;
  return `发现 ${images.length || '部分'} 张动图需要手动处理${overLimitCount ? `，其中 ${overLimitCount} 张超过微信 5MB 上限` : ''}。为了保护画质，插件没有自动生成低质量版本；点击下方“展开 ${images.length || '全部'} 张问题动图”查看位置和建议。`;
}

async function reloadDynamicState() {
  const stored = await chrome.storage.local.get([
    SOURCE_KEY,
    PACKAGE_KEY,
    STATUS_KEY,
    LAST_RESULT_KEY,
    PAGE_STATUS_KEY,
    WRITE_STATUS_KEY,
    STATIC_IMAGE_QUALITY_KEY,
    TITLE_IMAGE_BRAND_KEY
  ]);
  storedSource = stored[SOURCE_KEY] || null;
  storedPackage = stored[PACKAGE_KEY] || null;
  outdatedPackageDiscarded = Boolean(storedPackage && !ACCEPTED_STYLE_VERSIONS.has(storedPackage.styleVersion));
  outdatedPackageSourceUrl = outdatedPackageDiscarded ? storedPackage.sourceUrl : null;
  if (outdatedPackageDiscarded) {
    storedPackage = null;
    await chrome.storage.local.remove(PACKAGE_KEY);
  }
  compileStatus = stored[STATUS_KEY] || null;
  wechatPageStatus = stored[PAGE_STATUS_KEY] || null;
  wechatWriteStatus = stored[WRITE_STATUS_KEY] || null;
  staticImageQuality = normalizedStaticImageQuality(stored[STATIC_IMAGE_QUALITY_KEY]);
  staticImageQualitySelect.value = String(staticImageQuality);
  titleImageBrandPreference = normalizedTitleImageBrand(stored[TITLE_IMAGE_BRAND_KEY]);
  titleImageBrandSelect.value = titleImageBrandPreference;
  const staleReason = writeGuard.staleWriteReason(wechatWriteStatus, wechatPageStatus);
  if (staleReason) {
    await failStaleWechatWrite(staleReason);
    stored[WRITE_STATUS_KEY] = wechatWriteStatus;
  }
  return stored;
}

async function refreshServiceHealth() {
  const response = await chrome.runtime.sendMessage({ type: 'IFANR_SERVICE_HEALTH' })
    .catch(() => ({ ok: false }));
  const directReaderAvailable = Boolean(sourceLink.parseFeishuDocUrl(activeTab?.url));
  if (directReaderAvailable && response?.ok) {
    serviceIndicator.dataset.state = 'online';
    serviceIndicator.textContent = '浏览器直读 + 增强服务';
  } else if (directReaderAvailable) {
    serviceIndicator.dataset.state = 'online';
    serviceIndicator.textContent = '浏览器直读可用';
  } else if (storedPackage?.readerMode === 'browser-session') {
    serviceIndicator.dataset.state = 'online';
    serviceIndicator.textContent = '已用浏览器直读';
  } else if (response?.ok) {
    serviceIndicator.dataset.state = 'online';
    serviceIndicator.textContent = '增强服务在线';
  } else {
    serviceIndicator.dataset.state = 'offline';
    serviceIndicator.textContent = '增强服务未连接';
  }
  return response;
}

function renderLastResult(lastResult) {
  if (!lastResult) return;
  const report = lastResult.result || {};
  if (lastResult.ok && report.ok) {
    const hardLimitCount = Number(report.manualImagePlaceholderCount || 0);
    const hostingFallbackCount = Number(report.hostingFallbackPlaceholderCount || 0);
    const manualCount = hardLimitCount + hostingFallbackCount;
    const manualOrders = [...new Set([
      ...(Array.isArray(report.manualImageOrders) ? report.manualImageOrders : []),
      ...(Array.isArray(report.hostingFallbackImageOrders) ? report.hostingFallbackImageOrders : [])
    ])].sort((a, b) => a - b);
    if (report.styleValidationBypassed || report.layoutStyleConfirmed === false) {
      showResult({
        title: manualCount ? '已强制覆盖，请检查样式并补图' : '已强制覆盖，请检查样式',
        copy: `正文、图片和保存流程已经完成；样式差异只作为提醒，不会回滚内容。请在发布前快速检查标题、正文和引用块。${manualCount ? `另有 ${manualCount} 张图片已在原位置标记待补。` : ''}`,
        tone: 'warning',
        detail: lastResult
      });
      return;
    }
    if (manualCount > 0) {
      showResult({
        title: `正文已保存，${manualCount} 张图片待手动补充`,
        copy: `其余 ${report.visibleHostedImageCount || 0} 张图片已完成托管。超限或未完成微信托管的图片已在原位置留下橙色标记${manualOrders.length ? `（第 ${manualOrders.join('、')} 张）` : ''}，请检查后手动替换。`,
        tone: 'warning',
        detail: lastResult
      });
      return;
    }
    const imageCopy = report.visibleHostedImageCount == null ? '' : `，${report.visibleHostedImageCount} 张图片已完成托管`;
    showResult({
      title: '排版完成，草稿已保存',
      copy: `正文样式已确认写入公众号${imageCopy}。可以继续预览和编辑。`,
      tone: 'success',
      detail: lastResult
    });
    return;
  }
  const error = lastResult.error || 'UNKNOWN';
  const pending = Number(report.pendingEmbeddedImageCount || 0);
  const pendingAnimated = Number(report.pendingAnimatedImageCount || 0);
  const pendingOrders = Array.isArray(report.pendingImageOrders) ? report.pendingImageOrders : [];
  const copy = error === 'WECHAT_SAVE_NOT_CONFIRMED'
    ? report.waitStoppedReason === 'save-status-stalled'
      ? '正文和图片已经写入，但微信在 5 秒内没有返回新的保存状态，插件已停止等待。请直接查看页面底部是否显示“已保存”。'
      : '内容已经写入，但微信没有返回明确的保存状态。请保持页面打开并确认“已保存”。'
    : error === 'WECHAT_EDITOR_CLEAR_NOT_CONFIRMED'
      ? '公众号正文根节点无法直接替换，请刷新编辑页后重试。'
    : error === 'WECHAT_STYLE_NOT_CONFIRMED'
      ? `新内容没有通过样式和根节点隔离校验，插件已尝试恢复写入前的草稿。已检测到 ${report.headingStyleCount || 0} 个标题样式、${report.bodyStyleCount || 0} 个正文样式。`
    : error === 'WECHAT_IMAGE_UPLOAD_NOT_CONFIRMED'
      ? `${report.waitStoppedReason === 'image-hosting-stalled' ? '图片托管连续 10 秒没有进展，插件已停止等待。' : ''}仍有 ${pending || '部分'} 张${pendingAnimated ? '动图' : '图片'}没有完成微信托管。${pendingOrders.length ? `失败位置：第 ${pendingOrders.join('、')} 张。` : '重新收录后再排版即可。'}`
      : '本次排版没有完整通过校验，请查看页面提示后重试。';
  const title = error === 'WECHAT_STYLE_NOT_CONFIRMED'
    ? '样式写入未完成'
    : error === 'WECHAT_EDITOR_CLEAR_NOT_CONFIRMED'
      ? '编辑器无法覆盖'
    : error === 'WECHAT_IMAGE_UPLOAD_NOT_CONFIRMED'
    ? `正文已保存，${pending || '部分'} 张图片未完成`
    : '本次排版发现问题';
  showResult({ title, copy, tone: 'warning', detail: lastResult });
}

function queueCompile(parsedSource) {
  const source = {
    ...parsedSource,
    title: cleanDisplayTitle(activeTab.title) || parsedSource.token,
    tabId: activeTab.id,
    capturedAt: new Date().toISOString(),
    options: { allowRiskyGifs: true, staticImageQuality },
    staticImageQuality,
    titleImageBrand: titleImageBrandPreference
  };
  source.options.titleImageBrand = titleImageBrandPreference;

  return chrome.storage.local.set({ [SOURCE_KEY]: source }).then(async () => {
    storedSource = source;
    storedPackage = null;
    showSource(source);
    showPackage(null);
    hideResult();

    try {
      await navigator.clipboard.writeText(source.canonicalUrl);
    } catch {
      // Storage is authoritative; clipboard is only a convenience.
    }

    setStatus({
      step: '步骤 1 / 2',
      tag: '处理中',
      title: '正在生成排版内容',
      copy: '已记录当前飞书文档，正在使用当前 Chrome 页面读取正文和图片；页面直读失败时才会尝试本机增强服务。',
      tone: 'neutral'
    });
    const acceptedStatus = {
      state: 'processing',
      phase: 'accepted',
      sourceUrl: source.canonicalUrl,
      startedAt: new Date().toISOString(),
      deadlineAt: new Date(Date.now() + 45000).toISOString(),
      progress: { phase: 'accepted', percent: 1, message: '任务已收录，正在读取当前飞书页面' }
    };
    compileStatus = acceptedStatus;
    showCompileProgress(acceptedStatus);
    showPackage({ blockCount: '处理中', imageCount: 0 }, '生成中');
    setPrimary('正在生成排版内容…', null, false);
    showResult({
      title: '可以先关闭弹窗',
      copy: '排版会在后台继续进行，完成后扩展图标会出现完成标记。',
      tone: 'neutral',
      detail: { state: 'accepted', sourceUrl: source.canonicalUrl, acceptedAt: new Date().toISOString() }
    });

    chrome.runtime.sendMessage({ type: 'IFANR_COMPILE_FEISHU', source })
      .catch((error) => showResult({
        title: '后台任务没有启动',
        copy: error.message || '请重新打开插件后重试。',
        tone: 'danger',
        detail: { error: error.message }
      }));
  });
}

async function recheckWechatEditorTabs() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  activeTab = tab;
  wechatEditorTabs = await queryWechatEditorTabs();
  const stored = await reloadDynamicState();
  renderCurrentView(stored);
}

function renderMultipleWechatEditors() {
  hideCompileProgress();
  setStatus({
    step: '步骤 2 / 2',
    tag: '已暂停',
    title: '请只保留一个公众号编辑页',
    copy: `检测到 ${wechatEditorTabs.length} 个微信公众号图文编辑页。为避免自动保存互相覆盖，插件不会开始或继续写入。`,
    tone: 'warning'
  });
  showPackage(storedPackage, '等待处理');
  setPrimary('关闭其他编辑页后重新检查', recheckWechatEditorTabs);
  showResult({
    title: '已阻止多页面写入',
    copy: '请关闭其他公众号图文编辑页，只保留当前目标草稿，再点击重新检查。插件不会自动关闭页面，也不会修改当前草稿。',
    tone: 'warning',
    detail: {
      error: 'MULTIPLE_WECHAT_EDITORS',
      editorTabCount: wechatEditorTabs.length,
      activeTabId: activeTab?.id || null
    }
  });
}

async function syncStoredPackageToWechat() {
  const articlePackage = storedPackage;
  if (!articlePackage) throw new Error('ARTICLE_PACKAGE_NOT_READY');
  wechatEditorTabs = await queryWechatEditorTabs();
  if (wechatEditorTabs.length > 1) {
    renderMultipleWechatEditors();
    return;
  }
  const manualImageCount = manualImageReplacementsForPackage(articlePackage).length;
  actionRunning = true;
  setStatus({
    step: '步骤 2 / 2',
    tag: '写入中',
    title: '正在排入微信公众号',
    copy: articlePackage.imageCount > 0
      ? manualImageCount
        ? `正在写入正文并托管 ${articlePackage.imageCount - manualImageCount} 张图片；${manualImageCount} 张超限动图会在原位置标记待补。`
        : `正在写入正文并托管 ${articlePackage.imageCount} 张图片，请保持当前页面打开。`
      : `正在写入 ${articlePackage.blockCount} 个文字内容块，请保持当前页面打开。`,
    tone: 'neutral'
  });
  setPrimary('正在排版，请稍候…', null, false);
  const requestId = globalThis.crypto?.randomUUID?.() || String(Date.now());
  const startedAt = new Date().toISOString();
  wechatWriteStatus = {
    state: 'processing',
    phase: 'preparing-write',
    requestId,
    sourceUrl: articlePackage.sourceUrl,
    startedAt,
    deadlineAt: new Date(Date.now() + 45000).toISOString(),
    progress: { phase: 'preparing-write', percent: 1, message: '正在准备公众号编辑器' }
  };
  await chrome.storage.local.set({ [WRITE_STATUS_KEY]: wechatWriteStatus });
  showCompileProgress(wechatWriteStatus);
  showResult({
    title: '正在净空并写入草稿',
    copy: '插件会直接覆盖当前正文；图片 8 秒无进展或保存状态 3 秒无返回时会立即结束等待。',
    tone: 'neutral',
    detail: { state: 'syncing', requestId, startedAt }
  });
  await chrome.storage.local.remove(LAST_RESULT_KEY);
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const response = await chrome.tabs.sendMessage(tab.id, {
    type: 'IFANR_INJECT_HTML',
    requestId,
    sourceUrl: articlePackage.sourceUrl,
    html: articlePackage.html,
    options: packageOptions(articlePackage)
  }).catch((error) => ({ ok: false, error: error.message }));
  actionRunning = false;
  hideCompileProgress();
  renderLastResult(response);
  if (response?.ok) {
    const manualCount = Number(response.result?.manualImagePlaceholderCount || 0) +
      Number(response.result?.hostingFallbackPlaceholderCount || 0);
    const styleBypassed = Boolean(response.result?.styleValidationBypassed || response.result?.layoutStyleConfirmed === false);
    const metadataIncomplete = response.result?.metadataConfirmed === false;
    setStatus({
      step: '步骤 2 / 2',
      tag: styleBypassed || metadataIncomplete ? '需检查' : manualCount ? '需要补图' : '已完成',
      title: metadataIncomplete
        ? '正文已保存，请检查标题和摘要'
        : styleBypassed ? manualCount ? '已强制覆盖，请检查样式并补图' : '已强制覆盖，请检查样式' : manualCount ? `正文已保存，${manualCount} 张动图待补` : '排版完成，草稿已保存',
      copy: styleBypassed
        ? `正文已经直接覆盖并保存；样式差异只作为提醒，请在发布前快速检查标题、正文和引用块。${manualCount ? `另有 ${manualCount} 张超限图片需要手动替换。` : ''}`
        : metadataIncomplete
          ? '正文和图片已经写入，但当前微信页面没有确认标题或摘要输入框；请在发布前补充检查。'
        : manualCount
        ? '超限或未完成微信托管的图片已在原位置留下标记；请检查并手动替换，其他内容已经保存。'
        : '微信已经确认保存，可以继续预览、补充封面或进行人工检查。',
      tone: styleBypassed || metadataIncomplete || manualCount ? 'warning' : 'success'
    });
    setPrimary('重新排入当前草稿', syncStoredPackageToWechat);
  } else {
    setStatus({
      step: '步骤 2 / 2',
      tag: '发现问题',
      title: response?.error === 'WECHAT_IMAGE_UPLOAD_NOT_CONFIRMED'
        ? '正文已保存，图片未全部完成'
        : response?.error === 'WECHAT_EDITOR_CLEAR_NOT_CONFIRMED'
          ? '编辑器无法覆盖'
        : response?.error === 'WECHAT_STYLE_NOT_CONFIRMED'
          ? '样式写入失败'
          : '本次排版需要检查',
      copy: response?.error === 'WECHAT_IMAGE_UPLOAD_NOT_CONFIRMED'
        ? '图片托管连续 8 秒没有进展时会立即停止；技术详情会标出尚未完成的图片。'
        : response?.error === 'WECHAT_EDITOR_CLEAR_NOT_CONFIRMED'
          ? '插件没有找到可安全替换的正文根节点，请刷新公众号编辑页后重试。'
        : response?.error === 'WECHAT_STYLE_NOT_CONFIRMED'
          ? '正文写入本身失败，请刷新公众号编辑页后重试。'
        : '内容可能已经写入，但尚未完整通过保存和图片托管校验。',
      tone: 'warning'
    });
    setPrimary('重新尝试排版', syncStoredPackageToWechat);
  }
}

function renderFeishuPage(parsedSource) {
  showSource({ ...parsedSource, title: cleanDisplayTitle(activeTab.title) || parsedSource.token });
  showPageNotice(null);

  if (matchesSource(storedPackage, parsedSource)) {
    const manualImageCount = manualImageReplacementsForPackage(storedPackage).length;
    const specialBlockCount = Number(storedPackage.contentWarnings?.length || 0);
    const imageWarnings = [...(storedPackage.gifWarnings || []), ...(storedPackage.mediaWarnings || [])];
    const packageNeedsReview = Boolean(imageWarnings.length || specialBlockCount);
    hideCompileProgress();
    setStatus({
      step: '步骤 1 / 2',
      tag: packageNeedsReview ? '需要抽检' : '已就绪',
      title: imageWarnings.length
        ? '排版已就绪，问题图片已标出'
        : specialBlockCount
          ? '内容已准备，请抽检特殊内容块'
          : '排版内容已经准备完成',
      copy: imageWarnings.length
        ? manualImageCount
          ? `正文和其他图片已准备完成；${manualImageCount} 张超过微信 5MB 的图片将在原位置标记待补，不会阻断排版。`
          : `正文和其他图片已准备完成；${imageWarnings.length} 张图片保留原始质量并列为提醒。`
        : specialBlockCount
          ? `发现 ${specialBlockCount} 个表格、附件或其他特殊内容块，已转为普通段落；写入微信后请重点抽检。`
          : `正文和图片已安全缓存，已使用${titleImageBrandLabel(storedPackage) || '默认题图'}。现在前往微信公众号编辑页，打开插件完成排版。`,
      tone: packageNeedsReview ? 'warning' : 'success'
    });
    showPackage(storedPackage, '已就绪');
    setPrimary('重新收录当前文档', () => queueCompile(parsedSource));
    if (imageWarnings.length) {
      showResult({
        title: '发现问题图片，排版仍可继续',
        copy: manualImageCount
          ? `插件不会生成明显低画质版本。${manualImageCount} 张超过 5MB 的图片会在正文原位置留下待补标记，其余内容正常写入。`
          : '插件会保留这些图片的质量，并继续写入正文、样式和其他图片。',
        tone: 'warning',
        detail: { mediaWarnings: imageWarnings }
      });
    } else if (specialBlockCount) {
      showResult({
        title: '特殊内容块需要抽检',
        copy: `共 ${specialBlockCount} 处已转为普通段落。表格、附件、嵌入卡片等复杂结构不会被冒充为完全保真。`,
        tone: 'warning',
        detail: { contentWarnings: storedPackage.contentWarnings }
      });
    }
    return;
  }

  if (outdatedPackageDiscarded && (
    !outdatedPackageSourceUrl || sourceLink.sameFeishuDoc(outdatedPackageSourceUrl, parsedSource.canonicalUrl)
  )) {
    hideCompileProgress();
    setStatus({
      step: '步骤 1 / 2',
      tag: '需要更新',
      title: '请重新收录当前文档',
      copy: '旧内容包使用了容易被微信重写的标签结构。重新收录后会改用新版兼容样式。',
      tone: 'warning'
    });
    showPackage(null);
    setPrimary('重新收录当前文档', () => queueCompile(parsedSource));
    return;
  }

  if (matchesSource(compileStatus, parsedSource) && compileStatus.state === 'processing') {
    setStatus({
      step: '步骤 1 / 2',
      tag: '处理中',
      title: '正在生成排版内容',
      copy: '当前飞书文档已经记录，后台仍在读取正文并整理图片。可以关闭弹窗，完成后扩展图标会出现完成标记。',
      tone: 'neutral'
    });
    showPackage({ blockCount: compileStatus.blockCount || '处理中', imageCount: compileStatus.imageCount || 0 }, '生成中');
    showCompileProgress(compileStatus);
    setPrimary('正在生成排版内容…', null, false);
    return;
  }

  if (matchesSource(compileStatus, parsedSource) && compileStatus.state === 'failed') {
    hideCompileProgress();
    const qualityProtected = compileStatus.error?.code === 'GIF_MANUAL_OPTIMIZATION_REQUIRED';
    setStatus({
      step: '步骤 1 / 2',
      tag: '读取失败',
      title: qualityProtected ? '旧版检测结果需要重新收录' : '这次收录没有完成',
      copy: compileErrorSummary(compileStatus),
      tone: 'danger'
    });
    showPackage(null);
    setPrimary('重新收录当前文档', () => queueCompile(parsedSource));
    const qualityIssueCount = Array.isArray(compileStatus.error?.images) ? compileStatus.error.images.length : 0;
    showResult({
      title: qualityProtected ? '升级后将自动继续排版' : '错误详情',
      copy: qualityProtected
        ? `这是旧版留下的中断状态。重新收录后，${qualityIssueCount || '这些'} 张问题动图会直接标出，超过 5MB 的图片会在原位置留下待补标记，不再要求二次确认。`
        : '修复对应问题后，可以直接重新收录。',
      tone: qualityProtected ? 'warning' : 'danger',
      detail: compileStatus
    });
    return;
  }

  setStatus({
    step: '步骤 1 / 2',
    tag: '等待收录',
    title: '收录当前飞书文档',
      copy: '点击后会通过当前 Chrome 中已经打开的飞书页面读取全文，不需要单独登录飞书 CLI。',
    tone: 'neutral'
  });
  hideCompileProgress();
  showPackage(null);
  setPrimary('收录当前飞书文档', () => queueCompile(parsedSource));
}

function renderWechatPage(lastResult) {
  showSource(storedSource);
  const activeDraftKey = sourceLink.wechatEditorKey(activeTab?.url);
  showPageNotice(wechatPageStatus?.draftKey === activeDraftKey ? wechatPageStatus : null);

  if (wechatEditorTabs.length > 1) {
    renderMultipleWechatEditors();
    return;
  }

  const recoverableWriteFailure = matchesSource(wechatWriteStatus, storedSource) && writeGuard.isRecoverableFailure(wechatWriteStatus);
  const completedResult = matchesSource(lastResult, storedSource) && lastResult?.ok && lastResult?.result?.ok;
  const manualResultCount = completedResult ? Number(lastResult.result?.manualImagePlaceholderCount || 0) : 0;

  if (!storedSource) {
    hideCompileProgress();
    setStatus({
      step: '步骤 2 / 2',
      tag: '缺少来源',
      title: '还没有收录飞书文档',
      copy: '请先打开目标飞书文档，点击插件完成收录。',
      tone: 'warning'
    });
    showPackage(null);
    setPrimary('请先在飞书完成收录', null, false);
  } else if (matchesSource(compileStatus, storedSource) && compileStatus.state === 'processing') {
    setStatus({
      step: '步骤 2 / 2',
      tag: '生成中',
      title: '排版内容仍在准备',
      copy: '飞书文档已经收录，后台正在生成排版内容，完成后这里会自动更新。',
      tone: 'neutral'
    });
    showPackage({ blockCount: compileStatus.blockCount || '处理中', imageCount: compileStatus.imageCount || 0 }, '生成中');
    showCompileProgress(compileStatus);
    setPrimary('正在生成排版内容…', null, false);
  } else if (!matchesSource(storedPackage, storedSource)) {
    hideCompileProgress();
    const failed = matchesSource(compileStatus, storedSource) && compileStatus.state === 'failed';
    setStatus({
      step: '步骤 2 / 2',
      tag: failed ? '读取失败' : '尚未就绪',
      title: failed ? '飞书内容没有读取完成' : '排版内容还没有准备好',
      copy: failed ? readableCompileError(compileStatus) : '请回到飞书文档页重新打开插件完成收录。',
      tone: failed ? 'danger' : 'warning'
    });
    showPackage(null);
    setPrimary('请回到飞书重新收录', null, false);
  } else if (matchesSource(wechatWriteStatus, storedSource) && wechatWriteStatus.state === 'processing') {
    const progress = wechatWriteStatus.progress || {};
    setStatus({
      step: '步骤 2 / 2',
      tag: '写入中',
      title: phaseLabel(progress.phase || wechatWriteStatus.phase),
      copy: progress.message || '正在把飞书内容排入当前公众号草稿。',
      tone: 'neutral'
    });
    showPackage(storedPackage, '写入中');
    showCompileProgress(wechatWriteStatus);
    setPrimary('正在写入公众号…', null, false);
  } else if (recoverableWriteFailure) {
    const refreshed = wechatWriteStatus.error?.code === 'WECHAT_EDITOR_RELOADED';
    hideCompileProgress();
    setStatus({
      step: '步骤 2 / 2',
      tag: '写入已停止',
      title: refreshed ? '微信刷新已中断本次排版' : '公众号写入已经超时',
      copy: refreshed
        ? '旧任务不会继续等待。请确认只保留当前一个编辑页，并检查现有草稿内容后再重新排版。'
        : '插件已停止旧任务，避免一直卡在准备状态。请检查当前草稿后重新尝试。',
      tone: 'warning'
    });
    showPackage(storedPackage, '等待重试');
    setPrimary('重新尝试排版', syncStoredPackageToWechat);
    showResult({
      title: '本次写入已经终止',
      copy: refreshed
        ? '微信在写入时刷新或重新载入了编辑器。请先检查草稿，确认没有重复内容，再重新尝试。'
        : '写入超过 45 秒仍未完成，插件已经结束等待。请检查草稿后重新尝试。',
      tone: 'warning',
      detail: wechatWriteStatus
    });
  } else if (completedResult) {
    hideCompileProgress();
    const metadataIncomplete = lastResult.result?.metadataConfirmed === false;
    setStatus({
      step: '步骤 2 / 2',
      tag: metadataIncomplete ? '需检查' : manualResultCount ? '需要补图' : '已完成',
      title: metadataIncomplete ? '正文已保存，请检查标题和摘要' : manualResultCount ? `正文已保存，${manualResultCount} 张动图待补` : '排版完成，草稿已保存',
      copy: metadataIncomplete
        ? '正文和图片已经写入，但当前微信页面没有确认标题或摘要输入框；请在发布前补充检查。'
        : manualResultCount
        ? '超限动图已在原位置留下橙色标记；请压缩到 5MB 内后手动替换。'
        : '正文、图片和排版样式均已确认，可以继续人工检查。',
      tone: metadataIncomplete || manualResultCount ? 'warning' : 'success'
    });
    showPackage(storedPackage, metadataIncomplete ? '需检查' : manualResultCount ? '需要补图' : '已完成');
    setPrimary('重新排入当前草稿', syncStoredPackageToWechat);
  } else {
    hideCompileProgress();
    setStatus({
      step: '步骤 2 / 2',
      tag: '可以排版',
      title: '内容已就绪，等待写入',
      copy: '点击后会直接净空当前正文并写入已经收录的飞书内容，不再要求二次确认。',
      tone: 'neutral'
    });
    showPackage(storedPackage, '已就绪');
    setPrimary('一键覆盖并排版', syncStoredPackageToWechat);
    const imageWarnings = [...(storedPackage.gifWarnings || []), ...(storedPackage.mediaWarnings || [])];
    if (imageWarnings.length && !lastResult) {
      const manualImageCount = manualImageReplacementsForPackage(storedPackage).length;
      showResult({
        title: '这次排版含问题图片',
        copy: manualImageCount
          ? `${imageWarnings.length} 张图片存在适配风险，其中 ${manualImageCount} 张超过微信 5MB 上限。超限图片会在原位置留下待补标记，不再静默掉图。`
          : `${imageWarnings.length} 张图片保留原始质量；正文、样式和其他图片会直接写入。`,
        tone: 'warning',
        detail: { mediaWarnings: imageWarnings }
      });
    }
  }

  if (!recoverableWriteFailure && matchesSource(lastResult, storedSource)) renderLastResult(lastResult);
}

function renderUnsupportedPage() {
  hideCompileProgress();
  showSource(storedSource);
  showPackage(matchesSource(storedPackage, storedSource) ? storedPackage : null);
  showPageNotice(null);
  setStatus({
    step: '工作入口',
    tag: '当前不可操作',
    title: '请打开飞书或微信公众号',
    copy: '在飞书文档页收录内容，在微信公众号图文编辑页完成排版。',
    tone: 'neutral'
  });
  setPrimary('当前页面不支持排版', null, false);
}

function renderCurrentView(stored) {
  const currentFeishuSource = sourceLink.parseFeishuDocUrl(activeTab?.url);
  qualityCard.hidden = !currentFeishuSource;
  if (currentFeishuSource) renderFeishuPage(currentFeishuSource);
  else if (sourceLink.isWechatEditorUrl(activeTab?.url)) renderWechatPage(stored?.[LAST_RESULT_KEY]);
  else renderUnsupportedPage();
}

async function initialize() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  activeTab = tab;
  wechatEditorTabs = await queryWechatEditorTabs();
  const stored = await reloadDynamicState();
  renderCurrentView(stored);
  void refreshServiceHealth();
}

injectButton.addEventListener('click', async () => {
  if (!currentAction || actionRunning) return;
  const action = currentAction;
  actionRunning = true;
  injectButton.disabled = true;
  try {
    await action();
  } catch (error) {
    showResult({
      title: '操作没有完成',
      copy: error.message || '请稍后重试。',
      tone: 'danger',
      detail: { error: error.message, at: new Date().toISOString() }
    });
  } finally {
    actionRunning = false;
    if (currentAction) injectButton.disabled = false;
  }
});

clearSourceButton.addEventListener('click', async () => {
  const reviewPackageKey = String(compileStatus?.reviewPackageKey || compileStatus?.error?.stagingKey || '');
  await chrome.storage.local.remove([
    SOURCE_KEY,
    PACKAGE_KEY,
    STATUS_KEY,
    LAST_RESULT_KEY,
    WRITE_STATUS_KEY,
    ...(reviewPackageKey.startsWith('ifanrArticlePackageStaging:') ? [reviewPackageKey] : [])
  ]);
  storedSource = null;
  storedPackage = null;
  compileStatus = null;
  wechatWriteStatus = null;
  hideResult();
  await initialize();
});

cancelCompileButton.addEventListener('click', async () => {
  cancelCompileButton.disabled = true;
  progressDetail.textContent = '正在停止任务…';
  const response = await chrome.runtime.sendMessage({ type: 'IFANR_CANCEL_COMPILE' })
    .catch((error) => ({ ok: false, error: { message: error.message } }));
  if (!response?.ok) {
    cancelCompileButton.disabled = false;
    progressDetail.textContent = response?.error?.message || '任务暂时无法停止，请稍后重试。';
  }
});

toggleGifIssuesButton.addEventListener('click', () => {
  const expanded = toggleGifIssuesButton.getAttribute('aria-expanded') === 'true';
  toggleGifIssuesButton.setAttribute('aria-expanded', String(!expanded));
  gifIssueList.hidden = expanded;
});

copyResultButton.addEventListener('click', async () => {
  const detail = result.textContent || '';
  if (!detail || detail === '等待操作') return;
  const originalLabel = copyResultButton.textContent;
  try {
    await navigator.clipboard.writeText(detail);
    copyResultButton.textContent = '已复制';
  } catch {
    copyResultButton.textContent = '复制失败';
  }
  setTimeout(() => {
    copyResultButton.textContent = originalLabel;
  }, 1400);
});

staticImageQualitySelect.addEventListener('change', async () => {
  staticImageQuality = normalizedStaticImageQuality(staticImageQualitySelect.value);
  staticImageQualitySelect.value = String(staticImageQuality);
  await chrome.storage.local.set({ [STATIC_IMAGE_QUALITY_KEY]: staticImageQuality });
});

titleImageBrandSelect.addEventListener('change', async () => {
  titleImageBrandPreference = normalizedTitleImageBrand(titleImageBrandSelect.value);
  titleImageBrandSelect.value = titleImageBrandPreference;
  await chrome.storage.local.set({ [TITLE_IMAGE_BRAND_KEY]: titleImageBrandPreference });

  const currentFeishuSource = sourceLink.parseFeishuDocUrl(activeTab?.url);
  if (!currentFeishuSource) return;
  if (compileStatus?.state === 'processing') {
    await chrome.runtime.sendMessage({ type: 'IFANR_CANCEL_COMPILE' }).catch(() => null);
  }
  await chrome.storage.local.remove([PACKAGE_KEY, STATUS_KEY, LAST_RESULT_KEY]);
  storedPackage = null;
  compileStatus = null;
  hideResult();
  await initialize();
});

function renderPreview() {
  serviceIndicator.dataset.state = 'online';
  serviceIndicator.textContent = '读取服务在线';
  showSource({
    title: '这幅 5999 元的眼镜，到底配不配当电竞玩家的新装备',
    canonicalUrl: 'https://ifanr.feishu.cn/wiki/preview'
  });
  clearSourceButton.hidden = true;
  showPackage({ blockCount: 60, imageCount: 16 }, '已就绪');
  hideCompileProgress();
  showPageNotice({ type: 'saved' });
  setStatus({
    step: '步骤 2 / 2',
    tag: '可以排版',
    title: '内容已就绪，等待写入',
    copy: '点击后会直接净空当前正文并写入已经收录的飞书内容。',
    tone: 'neutral'
  });
  setPrimary('排入当前公众号草稿', () => Promise.resolve());
  showResult({
    title: '排版完成，草稿已保存',
    copy: '正文已经写入公众号，16 张图片已完成托管。可以继续预览和编辑。',
    tone: 'success',
    detail: { preview: true, saved: true, visibleImageCount: 16 }
  });
}

if (globalThis.chrome?.storage?.local && globalThis.chrome?.runtime) {
  chrome.storage.onChanged.addListener(async (changes, areaName) => {
    if (areaName !== 'local') return;
    const relevant = [PACKAGE_KEY, STATUS_KEY, LAST_RESULT_KEY, PAGE_STATUS_KEY, WRITE_STATUS_KEY]
      .some((key) => Object.hasOwn(changes, key));
    if (!relevant) return;
    const stored = await reloadDynamicState();
    renderCurrentView(stored);
  });

  initialize().catch((error) => {
    setStatus({
      step: '初始化失败',
      tag: '无法继续',
      title: '插件暂时无法使用',
      copy: error.message || '请重新加载扩展后再试。',
      tone: 'danger'
    });
    setPrimary('无法继续', null, false);
    showResult({ title: '初始化错误', copy: '请重新加载扩展。', tone: 'danger', detail: { error: error.message } });
  });
} else {
  renderPreview();
}
