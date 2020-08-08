import { mount, Wrapper } from '@vue/test-utils';
import Vue from 'vue';
import Vuetify from 'vuetify';
import store from '@/store/store';
import UserSecuritySettings from '@/views/settings/UserSecuritySettings.vue';

Vue.use(Vuetify);

describe('UserSecuritySettings.vue', () => {
  let wrapper: Wrapper<UserSecuritySettings>;

  function createWrapper() {
    const vuetify = new Vuetify();
    return mount(UserSecuritySettings, {
      store,
      vuetify,
      stubs: ['v-tooltip']
    });
  }

  beforeEach(() => {
    wrapper = createWrapper();
  });

  test('displays no warning by default', async () => {
    expect(wrapper.find('.v-alert').exists()).toBe(false);
  });

  test('displays warning if premium sync enabled', async () => {
    store.commit('session/premiumSync', true);
    await wrapper.vm.$nextTick();
    expect(wrapper.find('.v-alert').exists()).toBe(true);
  });
});
