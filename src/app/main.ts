import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app.config';
import { DashboardComponent } from './features/dashboard/dashboard.component';

bootstrapApplication(DashboardComponent, appConfig)
  .catch((err) => console.error(err));