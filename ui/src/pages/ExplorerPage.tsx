import { useEffect, useState } from 'react'
import { api, type ClassInfo, type InterfaceInfo, type FileInfo } from '@/lib/api'
import { useProject } from '@/lib/project-context'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ClassTable } from '@/components/explorer/ClassTable'
import { InterfaceTable } from '@/components/explorer/InterfaceTable'
import { NamespaceList } from '@/components/explorer/NamespaceList'
import { FileTree } from '@/components/explorer/FileTree'

export function ExplorerPage() {
  const { selected } = useProject()
  const [classes, setClasses] = useState<ClassInfo[]>([])
  const [interfaces, setInterfaces] = useState<InterfaceInfo[]>([])
  const [namespaces, setNamespaces] = useState<string[]>([])
  const [files, setFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!selected) return
    setLoading(true)
    setClasses([])
    setInterfaces([])
    setNamespaces([])
    setFiles([])
    Promise.all([
      api.getClasses(selected).catch(() => []),
      api.getInterfaces(selected).catch(() => []),
      api.getNamespaces(selected).catch(() => []),
      api.getFiles(selected).catch(() => []),
    ]).then(([c, i, n, f]) => {
      setClasses(c)
      setInterfaces(i)
      setNamespaces(n)
      setFiles(f)
    }).finally(() => setLoading(false))
  }, [selected])

  if (!selected) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        Select a project to explore
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">{selected}</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Code explorer</p>
      </div>
      <Tabs defaultValue="classes">
        <TabsList>
          <TabsTrigger value="classes">
            Classes {!loading && classes.length > 0 && <span className="ml-1.5 text-xs opacity-70">({classes.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="interfaces">
            Interfaces {!loading && interfaces.length > 0 && <span className="ml-1.5 text-xs opacity-70">({interfaces.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="namespaces">
            Namespaces {!loading && namespaces.length > 0 && <span className="ml-1.5 text-xs opacity-70">({namespaces.length})</span>}
          </TabsTrigger>
          <TabsTrigger value="files">
            Files {!loading && files.length > 0 && <span className="ml-1.5 text-xs opacity-70">({files.length})</span>}
          </TabsTrigger>
        </TabsList>
        <TabsContent value="classes" className="mt-4">
          <ClassTable classes={classes} loading={loading} />
        </TabsContent>
        <TabsContent value="interfaces" className="mt-4">
          <InterfaceTable interfaces={interfaces} loading={loading} />
        </TabsContent>
        <TabsContent value="namespaces" className="mt-4">
          <NamespaceList namespaces={namespaces} loading={loading} />
        </TabsContent>
        <TabsContent value="files" className="mt-4">
          <FileTree files={files} loading={loading} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
