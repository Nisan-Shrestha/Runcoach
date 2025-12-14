import { createContext, useContext, useState, useEffect } from "react";
import { profileAPI } from "../services/api";

const UserContext = createContext();

export function UserProvider({ children }) {
  const [userProfile, setUserProfile] = useState({
    name: "",
    age: null,
    weight: null,
    height: null,
    experience_level: "beginner",
    weekly_mileage: null,
    goal: "5K",
    dietary_preference: "none",
    training_days: 3,
    location: "",
  });

  const [isProfileSaved, setIsProfileSaved] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const profile = await profileAPI.getProfile();
      if (profile && Object.keys(profile).length > 0) {
        setUserProfile(profile);
        setIsProfileSaved(true);
      }
    } catch (error) {
      console.error("Error loading profile:", error);
    }
  };

  const saveProfile = async (profile) => {
    try {
      await profileAPI.saveProfile(profile);
      setUserProfile(profile);
      setIsProfileSaved(true);
      return true;
    } catch (error) {
      console.error("Error saving profile:", error);
      return false;
    }
  };

  const updateProfile = (updates) => {
    setUserProfile((prev) => ({ ...prev, ...updates }));
  };

  return (
    <UserContext.Provider
      value={{
        userProfile,
        setUserProfile,
        updateProfile,
        saveProfile,
        isProfileSaved,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUserProfile() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUserProfile must be used within UserProvider");
  }
  return context;
}
