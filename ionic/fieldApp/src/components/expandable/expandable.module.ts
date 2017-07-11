import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ExpandableComponent } from './expandable';

@NgModule({
  declarations: [
    ExpandableComponent,
  ],
  imports: [
    IonicPageModule.forChild(ExpandableComponent),
  ],
  exports: [
    ExpandableComponent
  ]
})
export class ExpandableComponentModule {}
