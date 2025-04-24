"use client";

import { useState, useContext, createContext } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { toast } from "react-hot-toast";

type FieldType = "text" | "number" | "email" | "select" | "textarea";

interface Field {
  name: string;
  type: FieldType;
  label: string;
  options?: { label: string; value: string }[]; // for select fields
}

interface DynamicFormProps {
  fields: Field[];
  apiRoute: string;
  method: "POST" | "PUT" | "DELETE";
  title: string;
}

const FormContext = createContext<any>(null);

// 🔹 Function to get validation schema dynamically
const getFieldSchema = (field: Field) => {
  switch (field.type) {
    case "number":
      return z.number().min(1, `${field.label} is required`);
    case "email":
      return z.string().email("Invalid email");
    case "select":
      return z.string().min(1, `${field.label} is required`);
    case "textarea":
      return z.string().min(5, `${field.label} must be at least 5 characters`);
    default:
      return z.string().min(1, `${field.label} is required`);
  }
};

// 🔹 Dynamic fetch function for POST, PUT, DELETE
const fetchData = async (url: string, method: string, data?: any) => {
  try {
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: data ? JSON.stringify(data) : null,
    });

    if (!response.ok) throw new Error("Request failed");
    return await response.json();
  } catch (error) {
    console.error(error);
    throw error;
  }
};

const DynamicForm = ({ fields, apiRoute, method, title }: DynamicFormProps) => {
  const schema = z.object(
    fields.reduce((acc, field) => ({ ...acc, [field.name]: getFieldSchema(field) }), {})
  );

  const { state, setState } = useContext(FormContext);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) });

  const [loading, setLoading] = useState(false);

  const onSubmit = async (data: any) => {
    setLoading(true);
    try {
      await fetchData(apiRoute, method, method !== "DELETE" ? data : undefined);
      toast.success(`${title} successful!`);
      if (method === "DELETE") setState(null); // Remove item from context
    } catch (error) {
      toast.error("Action failed!");
    } finally {
      setLoading(false);
    }
  };

  const renderField = (field: Field) => {
    switch (field.type) {
      case "textarea":
        return <Textarea {...register(field.name)} className="w-full" />;
      case "select":
        return (
          <Select {...register(field.name)} className="w-full">
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        );
      default:
        return <Input type={field.type} {...register(field.name)} className="w-full" />;
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {fields.map((field) => (
          <div key={field.name}>
            <label className="block font-medium">{field.label}</label>
            {renderField(field)}
            {errors[field.name] && <p className="text-red-500 text-sm">{(errors[field.name] as any)?.message}</p>}
          </div>
        ))}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Processing..." : title}
        </Button>
      </form>
    </div>
  );
};

// 🔹 Context Provider to manage global form state
export const FormProvider = ({ children }: { children: React.ReactNode }) => {
  const [state, setState] = useState<any>(null);
  return <FormContext.Provider value={{ state, setState }}>{children}</FormContext.Provider>;
};

export default DynamicForm;
