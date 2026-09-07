(function (global) {
  const SCRIPT_FILES = {
    feishu: ['source-link.js', 'static-image-compression.js', 'title-image-brand.js', 'feishu-page-reader.js', 'feishu-content-script.js'],
    wechat: ['source-link.js', 'page-state.js', 'editor-adapter.js', 'content-script.js']
  };

  function connectionError(code, message) {
    return Object.assign(new Error(message), { code, beforeDispatch: true });
  }

  // Executed in the extension's isolated world. No document content is read.
  function probeReceiver(kind) {
    return { version: globalThis.__IFANR_RECEIVERS?.[kind] || null, href: location.href };
  }

  async function ensure(tabId, kind, expectedUrl) {
    const label = kind === 'wechat' ? '公众号' : '飞书';
    const tab = await chrome.tabs.get(tabId);
    const valid = kind === 'wechat'
      ? global.IFANR_SOURCE_LINK.isWechatEditorUrl(tab.url)
      : kind === 'feishu' && global.IFANR_SOURCE_LINK.parseFeishuDocUrl(tab.url);
    if (!valid) throw connectionError('PAGE_TARGET_INVALID', `请在${label}${kind === 'wechat' ? '图文编辑' : '文档'}页面打开插件。`);
    if (expectedUrl && tab.url !== expectedUrl) throw connectionError('PAGE_TARGET_CHANGED', '目标页面已切换，请回到原页面重新操作。');
    const version = chrome.runtime.getManifest().version;
    let initial;
    try {
      [initial] = await chrome.scripting.executeScript({target:{tabId, frameIds:[0]}, func:probeReceiver, args:[kind]});
    } catch {
      throw connectionError('PAGE_SCRIPT_ACCESS_DENIED', `无法连接${label}页面。请在扩展详情中允许访问该网站，再回到页面重试。`);
    }
    if (!initial?.documentId || initial.result?.href !== tab.url) {
      throw connectionError('PAGE_TARGET_CHANGED', '页面正在跳转，请等加载完成后重试。');
    }
    const documentId = initial.documentId;
    if (initial.result.version !== version) {
      try {
        await chrome.scripting.executeScript({target:{tabId, documentIds:[documentId]}, files:SCRIPT_FILES[kind]});
      } catch {
        throw connectionError('PAGE_SCRIPT_LOAD_FAILED', `${label}页面脚本补载失败。请确认网站访问权限，刷新页面后重试。`);
      }
    }
    const [ready] = await chrome.scripting.executeScript({target:{tabId, documentIds:[documentId]}, func:probeReceiver, args:[kind]});
    if (ready?.result?.version !== version || ready.result.href !== tab.url) {
      throw connectionError('PAGE_RECEIVER_NOT_READY', `${label}页面尚未连接成功，请刷新该页面后重试。`);
    }
    return {documentId};
  }

  async function send(tabId, kind, message, expectedUrl) {
    let target;
    try { target = await ensure(tabId, kind, expectedUrl); }
    catch (error) {
      if (error.beforeDispatch) throw error;
      throw connectionError('PAGE_CONNECTION_FAILED', '页面连接中断，本次指令尚未发送，请等页面加载完成后重试。');
    }
    // Pin the exact document. Never retry an action: a lost response may follow a successful write.
    try {
      const response = await chrome.tabs.sendMessage(tabId, message, target);
      if (!response || typeof response.ok !== 'boolean') throw new Error('Invalid response');
      return response;
    }
    catch (error) {
      throw Object.assign(new Error(kind === 'wechat'
        ? '排版指令发送后连接中断，请先检查当前草稿是否已写入，再决定是否重试。'
        : '读取指令发送后连接中断，请检查收录状态后重试。'),
      {code:'PAGE_ACTION_CONNECTION_LOST', beforeDispatch:false});
    }
  }

  global.IFANR_PAGE_CONNECTION = Object.freeze({ensure, send});
})(globalThis);
