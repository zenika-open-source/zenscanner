import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '@/views/Register.vue'
import Repositories from '../views/Repositories.vue'
import Secrets from '@/views/Secrets'
import Vulnerabilities from '@/views/Vulnerabilities'
import Repository from '@/views/Repository'
import Scan from '@/views/Scan'
import AccessTokens from '@/views/AccessTokens';
import NewRepository from '@/views/NewRepository'
import EditRepository from '@/views/EditRepository'
import AuthLayout from "@/layouts/Auth";
import Dashboard from "@/layouts/Dashboard";
import axios from 'axios'
import config from '@/config'

Vue.use(VueRouter)

const routes = [
  {
    path: "",
    component: Dashboard,
    beforeEnter: (_, __, next) => {
      let c = {headers:{"Authorization": "Bearer "+window.localStorage.getItem('access_token')}}
      axios.get(config.base_url+"/api/auth/me", c)
      .then(
      response => {
          if(response.status != 200) {
            return next({name: "login"})
          } else {
            return next();
          }
      }).catch(error => {
        if(error.response.status === 401) {
          return next({name: "login"})
        }
      })
    },
    children: [
      {
        path: "/access_tokens",
        name: "Access Tokens",
        component: AccessTokens,
        meta: {
          title: "Access Tokens",
        },
      },

      {
        path: "/repositories",
        name: "repositories",
        component: Repositories,
        meta: {
          title: "Repositories",
        },
      },
      {
        path: "/repositories/new",
        name: "new_repositories",
        component: NewRepository,
      },
      {
        path: '/repository/:repoUuid/edit',
        name: 'edit_repository',
        component: EditRepository,
      },
      
      {
        path: "/",
        name: "home",
        component: Home,
        meta: {
          title: "Home"
        },
      },
      {
        path: '/scan/:scanUuid',
        name: 'scan',
        component: Scan,
      },
      {
        path: '/repository/:repoUuid',
        name: 'repository',
        component: Repository,
        meta: {
          title: "Repository details"
        },
      },
      {
        path: "/secrets",
        name: "secrets",
        component: Secrets,
      },
      {
        path: "/vulnerabilities",
        name: "vulnerabilities",
        component: Vulnerabilities,
      },
    ],
  },
  {
    path: "/login",
    component: AuthLayout,
    children: [
      {
        path: "/login",
        name: "login",
        component: Login,
        meta: {
          title: "Login",
        },
      },
      {
        path: "/register",
        name: "register",
        component: Register
      }
    ],
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
