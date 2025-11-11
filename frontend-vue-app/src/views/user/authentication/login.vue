<script lang="ts" setup>
import type { ZayumFormSchema } from '@/_core/ui/common-ui';
import { computed, markRaw, ref, onMounted } from 'vue';
import { SliderCaptcha, z } from '@/_core/ui/common-ui';
import { AuthenticationLogin } from './components';
import SmsCodeInput from './components/SmsCodeInput.vue';
import QrCodeLogin from './components/QrCodeLogin.vue';
import { $t } from '@/locales';
import { useUserAuthStore } from '@/stores/user/auth';
import { useUserAccessStore } from '@/stores/user/access';
import * as UserAuthApi from '@/api/user/auth';

defineOptions({ name: 'Login' });

const authStore = useUserAuthStore();
const accessStore = useUserAccessStore();
const activeTab = ref('account'); // account/sms/qr/register/forgot/social

// 检查登录状态，已登录则跳转到首页
onMounted(async () => {
  console.log('Login页面初始化 - 开始检查登录状态');
  accessStore.initFromStorage();
  console.log('初始化后的accessStore状态:', {
    token: accessStore.userAccessToken,
    isValid: accessStore.isValidToken
  });

  if (accessStore.isValidToken) {
    console.log('检测到有效token，准备跳转');
    // 确保用户信息已加载
    await authStore.initFromStorage();
    console.log('加载后的用户信息:', authStore.userInfo);
    if (window.location.pathname !== '/user/login') {
      window.location.href = '/user/home';
    }
  } else {
    console.log('未检测到有效token，保持在登录页面');
    if (window.location.pathname !== '/user/login') {
      window.location.href = '/user/login';
    }
  }
});

const formSchema = computed((): ZayumFormSchema[] => {
  switch (activeTab.value) {
    case 'account': // 用户名密码登录
      return [
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.usernameTip') },
          fieldName: 'username',
          label: $t('authentication.username'),
          rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
        },
        {
          component: 'ZayumInputPassword',
          componentProps: { placeholder: $t('authentication.password') },
          fieldName: 'password',
          label: $t('authentication.password'),
          rules: z.string().min(1, { message: $t('authentication.passwordTip') }),
        },
        {
          component: markRaw(SliderCaptcha),
          fieldName: 'captcha',
          rules: z.boolean().refine((value) => value, {
            message: $t('authentication.verifyRequiredTip'),
          }),
        },
      ];
    
    case 'sms': // 手机验证码登录
      return [
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.phoneTip') },
          fieldName: 'phone',
          label: $t('authentication.phone'),
          rules: z.string().min(11, { message: $t('authentication.phoneTip') }),
        },
        {
          component: markRaw(SmsCodeInput),
          fieldName: 'code',
          label: $t('authentication.smsCode'),
          rules: z.string().min(6, { message: $t('authentication.smsCodeTip') }),
          componentProps: (formData: any) => ({
            phone: formData.phone
          })
        },
      ];

    case 'qr': // 二维码登录
      return [
        {
          component: markRaw(QrCodeLogin),
          fieldName: 'qrCode',
          label: $t('authentication.qrLogin'),
        },
      ];

    case 'register': // 注册
      return [
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.usernameTip') },
          fieldName: 'username',
          label: $t('authentication.username'),
          rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
        },
        {
          component: 'ZayumInputPassword',
          componentProps: { placeholder: $t('authentication.password') },
          fieldName: 'password',
          label: $t('authentication.password'),
          rules: z.string().min(6, { message: $t('authentication.passwordTip') }),
        },
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.phoneTip') },
          fieldName: 'phone',
          label: $t('authentication.phone'),
          rules: z.string().min(11, { message: $t('authentication.phoneTip') }),
        },
      ];

    case 'forgot': // 忘记密码
      return [
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.usernameTip') },
          fieldName: 'username',
          label: $t('authentication.username'),
          rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
        },
        {
          component: 'ZayumInputPassword',
          componentProps: { placeholder: $t('authentication.newPassword') },
          fieldName: 'newPassword',
          label: $t('authentication.newPassword'),
          rules: z.string().min(6, { message: $t('authentication.passwordTip') }),
        },
        {
          component: 'ZayumInput',
          componentProps: { placeholder: $t('authentication.smsCode') },
          fieldName: 'code',
          label: $t('authentication.smsCode'),
          rules: z.string().min(6, { message: $t('authentication.smsCodeTip') }),
        },
      ];

    default:
      return [];
  }
});

const handleSubmit = async (formData: any) => {
    try {
      let res;
      switch (activeTab.value) {
        case 'account':
          res = await UserAuthApi.loginApi({
            username: formData.username,
            password: formData.password,
            captcha: true
          });
          break;
        case 'sms':
          res = await UserAuthApi.smsLoginApi({
            phone: formData.phone,
            code: formData.code
          });
          break;
        case 'qr':
          res = await UserAuthApi.qrLoginApi(formData);
          break;
        case 'register':
          res = await UserAuthApi.registerApi(formData);
          break;
        case 'forgot':
          res = await UserAuthApi.forgotPasswordApi(formData);
          break;
        case 'social':
          // 第三方登录会跳转到授权页面
          break;
      }
      if (res?.access_token) {
        const accessStore = useUserAccessStore();
        console.log('登录成功，获取到token:', res.access_token);
        accessStore.setUserAccessToken(res.access_token);
        accessStore.setIsAccessChecked(true);
        console.log('已存储user token到accessStore');
        
        // 打印localStorage中的token验证存储
        console.log('localStorage token:', localStorage.getItem('userAccessToken'));
        console.log('localStorage expireTime:', localStorage.getItem('tokenExpireTime'));
        
        console.log('准备获取用户信息...');
        await authStore.fetchUserInfo();
        console.log('用户信息获取完成:', authStore.userInfo);
        
        // 确保用户信息已加载后再跳转
        if (authStore.userInfo) {
          window.location.href = '/user/home';
        } else {
          console.error('用户信息获取失败');
        }
      } else {
        console.error('登录响应中未找到access_token');
        return;
      }
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="login-container">
    <ZayumTabs v-model="activeTab">
      <ZayumTabPane key="account" :tab="$t('authentication.accountLogin')" />
      <ZayumTabPane key="sms" :tab="$t('authentication.smsLogin')" />
      <ZayumTabPane key="qr" :tab="$t('authentication.qrLogin')" />
      <ZayumTabPane key="register" :tab="$t('authentication.register')" />
      <ZayumTabPane key="forgot" :tab="$t('authentication.forgotPassword')" />
    </ZayumTabs>

    <AuthenticationLogin
      :form-schema="formSchema"
      :loading="authStore.loginLoading"
      @submit="handleSubmit"
    />

    <div v-if="activeTab !== 'social'" class="social-login">
      <ZayumDivider>{{ $t('authentication.socialLogin') }}</ZayumDivider>
      <div class="social-buttons">
        <ZayumButton @click="activeTab = 'social'">
          <template #icon><WechatOutlined /></template>
          {{ $t('authentication.wechatLogin') }}
        </ZayumButton>
        <ZayumButton @click="activeTab = 'social'">
          <template #icon><QqOutlined /></template>
          {{ $t('authentication.qqLogin') }}
        </ZayumButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}
.social-login {
  margin-top: 20px;
}
.social-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>
