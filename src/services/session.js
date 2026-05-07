import { computed, ref } from 'vue'

import { requestJson } from './api'

export const currentAccount = ref(null)
export const sessionReady = ref(false)
export const flashMessage = ref('')
export const flashType = ref('success')

export const isAuthenticated = computed(() => Boolean(currentAccount.value))

export async function loadSession(force = false) {
    if (sessionReady.value && !force) {
        return currentAccount.value
    }

    const { response, data } = await requestJson('/api/session')

    if (response.ok && data && data.authenticated) {
        currentAccount.value = data.account
    } else {
        currentAccount.value = null
    }

    sessionReady.value = true
    return currentAccount.value
}

export function setSessionAccount(account) {
    currentAccount.value = account
    sessionReady.value = true
}

export function setFlash(message, type = 'success') {
    flashMessage.value = message
    flashType.value = type
}

export function clearFlash() {
    flashMessage.value = ''
}

export async function logoutAccount() {
    const { response, data } = await requestJson('/api/logout', { method: 'POST' })

    if (response.ok) {
        currentAccount.value = null
        sessionReady.value = true
    }

    return { response, data }
}
