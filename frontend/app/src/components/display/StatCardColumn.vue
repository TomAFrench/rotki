<template>
  <dl>
    <dt
      class="title font-weight-regular"
      :class="lock ? 'd-flex justify-space-between' : ''"
    >
      <slot name="title"></slot>
    </dt>
    <dd class="primary--text text-h5 font-weight-bold">
      <slot></slot>
    </dd>
  </dl>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';

@Component({})
export default class StatCardColumn extends Vue {
  @Prop({ required: false, default: false, type: Boolean })
  lock!: boolean;
}
</script>

<style scoped></style>
