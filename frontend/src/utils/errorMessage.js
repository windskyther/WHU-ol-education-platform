const fieldMessageMap = {
  username: '用户名已存在或格式不正确',
  account: '账号不存在',
  email: '邮箱已被注册或格式不正确',
  registerEmail: '邮箱已被注册或格式不正确',
  password: '密码格式不正确',
  confirmPassword: '两次输入的密码不一致',
  confirm_password: '两次输入的密码不一致',
  password_confirm: '两次输入的密码不一致',
  email_code: '验证码错误或已过期',
  code: '验证码错误或已过期',
  role: '请选择正确的用户角色'
}

const networkMessages = new Set([
  '无法连接后端服务，请确认服务已启动',
  '请求超时，请稍后重试',
  '登录状态已失效，请重新登录',
  '当前账号没有操作权限',
  '服务器暂时不可用，请稍后重试'
])

function stringifyErrorData(value) {
  if (!value) return ''
  if (typeof value === 'string') return value
  if (Array.isArray(value)) return value.map(stringifyErrorData).join(' ')
  if (typeof value === 'object') {
    return Object.entries(value)
      .map(([key, item]) => `${key} ${stringifyErrorData(item)}`)
      .join(' ')
  }
  return String(value)
}

function getErrorText(error) {
  return stringifyErrorData(error?.rawData || error?.response?.data || error?.message || '')
}

function hasField(error, fields) {
  const data = error?.rawData?.data || error?.rawData || error?.response?.data?.data || error?.response?.data
  if (!data || typeof data !== 'object') return false
  return fields.some((field) => Object.prototype.hasOwnProperty.call(data, field))
}

function includesAny(text, keywords) {
  const lowerText = text.toLowerCase()
  return keywords.some((keyword) => lowerText.includes(keyword.toLowerCase()))
}

function isNetworkLevelMessage(message) {
  return networkMessages.has(message)
}

export function getLoginErrorMessage(error) {
  if (isNetworkLevelMessage(error?.userMessage)) return error.userMessage

  const text = getErrorText(error)

  if (includesAny(text, ['用户不存在', '账号不存在', '邮箱不存在', 'username not found', 'account not found', 'email not found', 'user not found', 'not found'])) {
    return '账号不存在'
  }

  if (includesAny(text, ['密码', 'password', 'credentials', 'unable to log in', 'no active account', 'invalid login', 'incorrect', 'invalid'])) {
    return '密码错误'
  }

  if ([400, 401].includes(error?.status) || [4000, 4001].includes(error?.businessCode || error?.code)) {
    return '账号或密码错误'
  }

  return error?.userMessage || '登录失败，请检查账号和密码'
}

export function getRegisterErrorMessage(error) {
  if (isNetworkLevelMessage(error?.userMessage)) return error.userMessage

  for (const [field, message] of Object.entries(fieldMessageMap)) {
    if (hasField(error, [field])) {
      return message
    }
  }

  const text = getErrorText(error)

  if (includesAny(text, ['USERNAME_EXISTS', '用户名', 'username', 'user name'])) return fieldMessageMap.username
  if (includesAny(text, ['EMAIL_EXISTS', '邮箱', 'email', 'registerEmail'])) return fieldMessageMap.email
  if (includesAny(text, ['CODE_', '验证码', 'email_code', 'verification', 'code', '过期', 'expired'])) return fieldMessageMap.email_code
  if (includesAny(text, ['PASSWORD_CONFIRM_MISMATCH', '确认密码', 'confirmPassword', 'confirm_password'])) return fieldMessageMap.confirmPassword
  if (includesAny(text, ['密码', 'password'])) return fieldMessageMap.password
  if (includesAny(text, ['角色', 'role'])) return fieldMessageMap.role

  return error?.userMessage || '注册失败，请检查填写信息'
}

export function getEmailCodeErrorMessage(error) {
  if (isNetworkLevelMessage(error?.userMessage)) return error.userMessage

  const text = getErrorText(error)

  if (hasField(error, ['email', 'registerEmail']) && includesAny(text, ['格式', 'invalid', 'valid'])) {
    return '请输入有效邮箱'
  }
  if (includesAny(text, ['EMAIL_EXISTS', '已注册', '已存在', 'exists', 'registered', 'duplicate'])) {
    return '该邮箱已被注册'
  }
  if (includesAny(text, ['CODE_COOLDOWN', '频繁', '冷却', '稍后', 'too many', 'rate', 'cooldown'])) {
    return '验证码发送太频繁，请稍后再试'
  }
  if (includesAny(text, ['EMAIL_SEND_FAILED', 'smtp', 'send failed'])) {
    return '邮件发送失败，请稍后重试'
  }
  if (includesAny(text, ['邮箱', 'email', 'registerEmail', 'invalid', 'valid'])) {
    return '请输入有效邮箱'
  }

  return error?.userMessage || '验证码发送失败，请稍后重试'
}

export function getCommonErrorMessage(error, fallback = '操作失败，请稍后重试') {
  return error?.userMessage || fallback
}
