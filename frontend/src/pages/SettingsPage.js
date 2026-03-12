import TopBar from "../components/layout/TopBar";

import PageHeader from "../components/common/PageHeader";

import SettingsSection from "../components/settings/SettingsSection";
import ProfileSettings from "../components/settings/ProfileSettings";
import CurrencySelector from "../components/settings/CurrencySelector";
import ThemeToggle from "../components/settings/ThemeToggle";
import PreferencesSettings from "../components/settings/PreferencesSettings";
import ConnectedAccounts from "../components/settings/ConnectedAccounts";

export default function SettingsPage() {

  return (

    <div>

      <TopBar />

      <PageHeader
        title="Settings"
        subtitle="Manage your preferences and integrations"
      />

      <SettingsSection title="Profile">

        <ProfileSettings />

      </SettingsSection>

      <SettingsSection title="Preferences">

        <div className="space-y-4">

          <CurrencySelector />

          <ThemeToggle />

          <PreferencesSettings />

        </div>

      </SettingsSection>

      <SettingsSection title="Connected Accounts">

        <ConnectedAccounts />

      </SettingsSection>

    </div>

  );

}