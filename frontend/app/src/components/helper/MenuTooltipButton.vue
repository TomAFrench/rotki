<template>
  <v-tooltip bottom z-index="215" class="tooltip-menu-button" open-delay="250">
    <template #activator="{ on: tooltip }">
      <v-btn
        icon
        :class="className"
        :retain-focus-on-click="retainFocusOnClick"
        v-on="{ ...tooltip, ...onMenu }"
      >
        <slot></slot>
      </v-btn>
    </template>
    <span>{{ tooltip }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';

@Component({})
export default class MenuTooltipButton extends Vue {
  @Prop({ required: true, default: '' })
  tooltip!: string;
  @Prop({ required: true, default: () => {} })
  onMenu!: () => void;
  @Prop({ required: false, default: false })
  retainFocusOnClick!: boolean;
  @Prop({ required: true, default: '' })
  className!: string;
}
</script>

<style scoped lang="scss">
// v-tooltip will render a span with a height computed to 0
// by v-menu, so we have to force a height here otherwise offset-y
// on the v-menu won't work

.tooltip-menu-button {
  display: block;
  height: 100%;
}
</style>
