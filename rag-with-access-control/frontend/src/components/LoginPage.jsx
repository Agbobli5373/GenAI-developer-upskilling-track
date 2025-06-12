import RoleSelector from "./RoleSelector";
import { Lock, Shield } from "lucide-react";
import "./LoginPage.css";

const LoginPage = ({ roles, selectedRole, onRoleSelect, onLogin, loading }) => {
  return (
    <div className="login-page">
      <div className="login-backdrop">
        <div className="login-circles">
          <div className="circle circle-1"></div>
          <div className="circle circle-2"></div>
          <div className="circle circle-3"></div>
        </div>
        
        <div className="login-container">
          <div className="login-header">
            <div className="login-logo">
              <Shield className="shield-icon" />
              <Lock className="lock-icon" />
            </div>
            <h1>Secure Access Portal</h1>
            <p>Select your role to access appropriate documents</p>
          </div>
          
          <RoleSelector
            roles={roles}
            selectedRole={selectedRole}
            onRoleSelect={onRoleSelect}
            onContinue={onLogin}
            loading={loading}
          />
          
          <div className="login-footer">
            <p>Protected by RAG with Access Control</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
