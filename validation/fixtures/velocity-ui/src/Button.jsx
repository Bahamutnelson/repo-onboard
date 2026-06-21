import React from "react";

// A presentational button. Library component — no app state, no data fetching.
export function Button({ variant = "primary", children, ...props }) {
  return (
    <button className={`vu-btn vu-btn--${variant}`} {...props}>
      {children}
    </button>
  );
}
