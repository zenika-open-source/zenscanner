export default {
    base_url: (typeof process.env.BACKEND_URL === 'undefined') ? '' : process.env.BACKEND_URL,
}