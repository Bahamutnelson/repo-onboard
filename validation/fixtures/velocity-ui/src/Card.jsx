import React from "react";

// A surface container. Pure presentational component.
export function Card({ title, children }) {
  return (
    <div className="vu-card">
      {title ? <div className="vu-card__title">{title}</div> : null}
      <div className="vu-card__body">{children}</div>
    </div>
  );
}
