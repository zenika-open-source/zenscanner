import axios from 'axios';
import config from '@/config'

function base() {
    return axios.create({
        baseURL: config.base_url+"/api/",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+window.localStorage.getItem('access_token')
        }
    })
}

export default {
    get: function(url, options){
        return base().get(url, options)
    },
    delete: function(url, options){
        return base().delete(url, options)
    },
    put: function(url, options){
        return base().put(url, options)
    },
    post: function(url, options){
        return base().post(url, options)
    }
    
}