import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { PanchayatsPage } from './panchayats';

@NgModule({
  declarations: [
    PanchayatsPage,
  ],
  imports: [
    IonicPageModule.forChild(PanchayatsPage),
  ],
  exports: [
    PanchayatsPage
  ]
})
export class PanchayatsPageModule {}
